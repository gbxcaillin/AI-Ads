"""The solution shot: start wide on her relief, push in slowly until the
dashboard owns the frame and she has drifted out of it.

Source: the blank-screen plate clip and the per-frame screen quads measured by
track_and_composite.py (clips/act4-quads.npy). In that clip her mouth opens on
a breath from 0.75 s to 3.75 s, which read as a second sigh, so the shot uses
the clip from 4.0 s (eyes closing, then a settled smile) and holds its last
frame for the rest; the push carries on as one smooth move across both.

Apparent zoom is one ease-in-out from the opening framing to the end framing.
The clip's own camera push supplies part of it while it runs; a digital crop
supplies the rest (so the move never kinks when the live part ends). Every
output frame is resampled once from the 480p source, and the dashboard is
warped straight into output pixels from its full-resolution render, so the
zoom never softens it. Background and quad share one transform, so the
measured fit holds.

    python3 spots/libertystone-one/dashboard/solution_push.py
Writes clips/act4-solution-push.mp4 (1280x716, 24 fps, 7.0 s) and
clips/act4-push-check.png.
"""
import subprocess, shutil, sys
from pathlib import Path
import cv2
import numpy as np
import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).parent))
from screen_warp import composite  # noqa: E402

ROOT = Path('spots/libertystone-one')
SRC = ROOT / 'clips/act4-solution-blank.mp4'
QUADS = np.load(str(ROOT / 'clips/act4-quads.npy'))      # source px, per frame
OUT = ROOT / 'clips/act4-solution-push.mp4'
FPS, DUR = 24, 7.0
START_F = 96                  # 4.0 s: eyes closing, then the settled smile (no open mouth)
END_FILL = 0.78               # at the end the screen spans this fraction of the frame width
OW = 1280

cap = cv2.VideoCapture(str(SRC))
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
cap.release()
h, w = frames[0].shape[:2]
oh = int(round(h * OW / w / 2)) * 2
N = int(round(DUR * FPS))
src_idx = [min(START_F + k, len(frames) - 1) for k in range(N)]      # live, then hold the last frame


def width(q):                 # screen width in px (mean of top and bottom edges)
    return 0.5 * (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3]))


def centre(q):
    return q.mean(0)


w0 = width(QUADS[src_idx[0]])
src_ratio = np.array([width(QUADS[i]) / w0 for i in src_idx])          # the clip's own push
d_end = END_FILL * w / width(QUADS[src_idx[-1]])                       # digital zoom needed at the end
s_end = src_ratio[-1] * d_end                                          # total apparent zoom at the end
t = np.arange(N) / (N - 1)
ease = 0.5 - 0.5 * np.cos(np.pi * t)                                    # slow in, slow out
apparent = 1.0 + (s_end - 1.0) * ease
digital = np.maximum(1.0, apparent / src_ratio)
c_end = centre(QUADS[src_idx[-1]])
print(f'clip push {src_ratio[-1]:.3f}x over {min(len(frames) - START_F, N) / FPS:.2f}s live; '
      f'digital {digital[0]:.2f} -> {digital[-1]:.2f}; total {s_end:.2f}x')

ff = shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{OW}x{oh}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
                        '-crf', '16', '-pix_fmt', 'yuv420p', str(OUT)], stdin=subprocess.PIPE)
rng = np.random.default_rng(7)
face_out_at = None
check, corners = [], []
for k in range(N):
    i = src_idx[k]
    d = digital[k]
    cw, ch = w / d, h / d
    # crop centre glides from the frame centre to the screen centre on the same ease
    cx = (1 - ease[k]) * (w / 2) + ease[k] * c_end[0]
    cy = (1 - ease[k]) * (h / 2) + ease[k] * c_end[1]
    x0 = float(np.clip(cx - cw / 2, 0, w - cw))
    y0 = float(np.clip(cy - ch / 2, 0, h - ch))
    sc = OW / cw
    M = np.float32([[sc, 0, -x0 * sc], [0, oh / ch, -y0 * oh / ch]])
    bg = cv2.warpAffine(frames[i], M, (OW, oh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    q = (QUADS[i] - np.float32([x0, y0])) * np.float32([sc, oh / ch])
    comp = composite(bg, q, soften=0.5, glow=0.9)
    comp = np.clip(comp.astype(np.float32) + rng.normal(0, 2.0, comp.shape), 0, 255).astype(np.uint8)
    enc.stdin.write(comp.tobytes())
    # her face sits left of x ~ 0.33 of the source frame: note when the crop leaves it
    if face_out_at is None and x0 > 0.30 * w:
        face_out_at = k / FPS
    if k in (0, N // 3, 2 * N // 3, N - 1):
        check.append(cv2.resize(comp, (480, int(480 * oh / OW))))
    if k in (0, N // 2, N - 1):                       # 4x zoom on each corner, for the fit check
        row = []
        for c in q:
            x, y = int(c[0]), int(c[1])
            crop = comp[max(0, y - 40):y + 40, max(0, x - 40):x + 40]
            crop = cv2.copyMakeBorder(crop, 0, 80 - crop.shape[0], 0, 80 - crop.shape[1], cv2.BORDER_CONSTANT)
            row.append(cv2.resize(crop, (240, 240), interpolation=cv2.INTER_NEAREST))
        corners.append(np.hstack(row))
enc.stdin.close()
enc.wait()
cv2.imwrite(str(ROOT / 'clips/act4-push-corners.png'), np.vstack(corners))
cv2.imwrite(str(ROOT / 'clips/act4-push-check.png'), np.vstack([np.hstack(check[:2]), np.hstack(check[2:])]))
print(f'wrote {OUT} {OW}x{oh} {N} frames; her face leaves the frame at ~{face_out_at:.2f}s'
      if face_out_at is not None else f'wrote {OUT}; face never fully leaves (crop x0 max {x0:.0f})')

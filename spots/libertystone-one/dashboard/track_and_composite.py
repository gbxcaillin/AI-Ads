"""Track the laptop lid through the generated push-in and composite the real
dashboard onto its screen in every frame.

The plate was animated with a BLANK screen, so the video model never redraws
the dashboard text. Everything is measured on the video frames themselves
(the model's frame 0 is close to the plate but not pixel-identical).

Per side of the lid, one straight edge is tracked: the dark-glass to
bright-rim step on top, left and bottom, and the rim-to-dark-wall step on the
right (at 480p the right rim has almost no inner contrast). In every frame,
starting from the previous frame, the edge is located on the side's normal at
sub-pixel precision (frames upscaled 2x), a robust line is fitted per side and
the four lines are intersected. All four lines lie on the lid plane, so the
homography from frame 0's lines to frame i's lines carries the screen quad.
The screen quad in frame 0 is the tracked quad with the right side moved in
by the measured rim width.

Run from the repo root:
    python3 spots/libertystone-one/dashboard/track_and_composite.py
Writes clips/act4-solution-tracked.mp4 (1280 wide), clips/act4-quads.npy and
clips/act4-fit-check.png (zoomed corners at start, middle and end).
"""
import subprocess, shutil, sys
from pathlib import Path
import cv2
import numpy as np
import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).parent))
from screen_warp import SCREEN, PLATE_SIZE, composite  # noqa: E402

ROOT = Path('spots/libertystone-one')
SRC = ROOT / 'clips/act4-solution-blank.mp4'
OUT = ROOT / 'clips/act4-solution-tracked.mp4'
OUT_W = 1280
UP = 2.0           # analysis upscale
STEP = 0.25        # profile sample spacing (analysis px)
SIDES = ['top', 'right', 'bottom', 'left']
T_RANGE = {0: (0.10, 0.90), 1: (0.10, 0.90), 2: (0.10, 0.90), 3: (0.10, 0.78)}  # left: clear of her hand

cap = cv2.VideoCapture(str(SRC))
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
cap.release()
h, w = frames[0].shape[:2]
grays = [cv2.GaussianBlur(cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), None, fx=UP, fy=UP,
                                     interpolation=cv2.INTER_CUBIC).astype(np.float32), (0, 0), 1.0)
         for f in frames]
init = SCREEN * np.float32([w / PLATE_SIZE[0], h / PLATE_SIZE[1]]) * UP


def normal(quad, a):
    p, q = quad[a], quad[(a + 1) % 4]
    d = (q - p) / np.linalg.norm(q - p)
    return p, q, np.float32([d[1], -d[0]])          # outward for TL, TR, BR, BL


def profiles(gray, quad, a, reach, n=64):
    p, q, nrm = normal(quad, a)
    t0, t1 = T_RANGE[a]
    ts = np.linspace(t0, t1, n)
    ss = np.arange(-reach, reach + 1e-6, STEP)
    base = p[None] + (q - p)[None] * ts[:, None]
    pts = base[:, None, :] + ss[None, :, None] * nrm[None, None, :]
    prof = cv2.remap(gray, pts[..., 0].astype(np.float32), pts[..., 1].astype(np.float32), cv2.INTER_LINEAR)
    return base, nrm, ss, np.gradient(prof, STEP, axis=1)


def locate(gray, quad, a, sign, reach):
    """Sub-pixel edge points on side a for the given polarity (+1 dark->bright outward)."""
    base, nrm, ss, grad = profiles(gray, quad, a, reach)
    g = grad * sign
    n = len(base)
    j = np.clip(g.argmax(1), 1, len(ss) - 2)
    peak = g[np.arange(n), j]
    g0, g1, g2 = g[np.arange(n), j - 1], peak, g[np.arange(n), j + 1]
    den = g0 - 2 * g1 + g2
    delta = np.where(np.abs(den) > 1e-6, 0.5 * (g0 - g2) / np.where(den == 0, 1, den), 0.0)
    s = ss[j] + np.clip(delta, -0.5, 0.5) * STEP
    ok = peak > 0.35 * np.median(peak)               # drop samples with no real edge
    return base[ok] + s[ok, None] * nrm[None], int(ok.sum())


def fit_lines(gray, quad, signs, reach):
    lines, rms = [], []
    for a in range(4):
        pts, cnt = locate(gray, quad, a, signs[a], reach)
        if cnt < 16:
            return None, None
        vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        p0, d = np.float64([x0, y0]), np.float64([vx, vy])
        nrm = np.float64([d[1], -d[0]])
        rms.append(float(np.median(np.abs((pts - p0) @ nrm))))
        lines.append((p0, d))
    return lines, rms


def intersect(lines):
    corners = []
    for a in range(4):
        (p1, d1), (p2, d2) = lines[(a - 1) % 4], lines[a]
        t = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
        corners.append(p1 + t[0] * d1)
    return np.float32(corners)


# frame 0: pick each side's polarity by the stronger edge in a wide search
signs = []
for a in range(4):
    _, _, _, grad = profiles(grays[0], init, a, reach=14.0)
    signs.append(1 if np.median(grad.max(1)) >= np.median((-grad).max(1)) else -1)
print('edge polarity per side:', dict(zip(SIDES, signs)))

# converge on frame 0 from the plate estimate with a wide search, then narrow
T0 = init
for reach in (14.0, 8.0, 5.0, 4.0):
    lines, rms = fit_lines(grays[0], T0, signs, reach)
    T0 = intersect(lines)

# The glass edge in frame 0, measured on every side: the dark-glass to bright-rim
# step (+1 polarity) searched only INSIDE the tracked line. Where a side tracks the
# rim's outer edge, this finds the rim's inner edge; where it already tracks the
# inner edge it lands on the same line.
def inner_line(gray, quad, a):
    base, nrm, ss, grad = profiles(gray, quad, a, reach=12.0)
    inside = ss <= 0.5
    g = np.where(inside[None], grad, -1e9)
    n = len(base)
    j = np.clip(g.argmax(1), 1, len(ss) - 2)
    peak = g[np.arange(n), j]
    s = ss[j]
    ok = peak > 0.35 * np.median(peak)
    pts = base[ok] + s[ok, None] * nrm[None]
    vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    off = float(np.median((pts - quad[a]) @ nrm))
    return (np.float64([x0, y0]), np.float64([vx, vy])), off, float(np.median(peak))

inner, offs = [], []
for a in range(4):
    ln, off, strength = inner_line(grays[0], T0, a)
    inner.append(ln); offs.append(off)
    print(f'  {SIDES[a]:6s} glass edge {-off / UP:5.2f} source px inside the tracked edge (step {strength:.0f})')
# At 480p the right side has no separate bright rim: the glass runs at one level
# right up to the lid edge, then falls to the dark wall. With no inner step to
# measure, put the glass edge just inside that falloff, so no band of the
# original glass shows and the 1 to 2 px falloff reads as the rim.
RIGHT_INSET = 0.9   # source px inside the tracked lid edge
_, _, strength_r = inner_line(grays[0], T0, 1)
if signs[1] < 0 and strength_r < 5:
    p, q, n1 = normal(T0, 1)
    shift = RIGHT_INSET * UP
    inner[1] = (np.float64(p - n1 * shift), np.float64((q - p) / np.linalg.norm(q - p)))
    print(f'  right  no inner step (strength {strength_r:.1f}); glass edge set {RIGHT_INSET} source px inside the lid edge')
S0 = intersect(inner)

Ts, fit_rms, fails = [T0], [rms], 0
prev2, prev = T0, T0
for i in range(1, len(grays)):
    pred = prev + (prev - prev2) * 0.5               # damped constant-velocity prediction
    lines, r = fit_lines(grays[i], pred, signs, reach=4.0)
    if lines is None:
        fails += 1
        T = pred
    else:
        T = intersect(lines)
        lines, r = fit_lines(grays[i], T, signs, reach=2.5)   # second, tighter pass
        T = intersect(lines) if lines is not None else T
    Ts.append(T); fit_rms.append(r if r is not None else [np.nan] * 4)
    prev2, prev = prev, T
print(f'tracked {len(Ts)} frames, {fails} fell back to prediction')

Ts = np.array(Ts)
Tsm = Ts.copy()
Tsm[1:-1] = (Ts[:-2] + 2 * Ts[1:-1] + Ts[2:]) / 4.0     # light smoothing of sub-pixel jitter
S = np.array([cv2.perspectiveTransform(S0.reshape(-1, 1, 2), cv2.getPerspectiveTransform(T0, Tsm[i])).reshape(-1, 2)
              for i in range(len(Tsm))]) / UP

R = np.array(fit_rms) / UP                                # source px
jit = np.abs(Ts - Tsm).max(axis=(1, 2)) / UP
sc = OUT_W / w
print('edge-fit residual, median distance of measured bezel points from each fitted side (source px):')
for a in range(4):
    print(f'  {SIDES[a]:6s} median {np.nanmedian(R[:, a]):.2f}  max {np.nanmax(R[:, a]):.2f}')
print(f'smoothing moved corners by at most {jit.max():.2f} source px ({jit.max() * sc:.2f} output px)')
np.save(str(ROOT / 'clips/act4-quads.npy'), S)

out_h = int(round(h * OUT_W / w / 2)) * 2
scale = np.float32([OUT_W / w, out_h / h])
ff = shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{OUT_W}x{out_h}', '-r', '24', '-i', '-', '-c:v', 'libx264',
                        '-crf', '16', '-pix_fmt', 'yuv420p', str(OUT)], stdin=subprocess.PIPE)
rng = np.random.default_rng(7)
check = []
for i, f in enumerate(frames):
    big = cv2.resize(f, (OUT_W, out_h), interpolation=cv2.INTER_LANCZOS4)
    q = S[i] * scale
    comp = composite(big, q, soften=0.6, glow=0.9)
    noise = rng.normal(0, 2.2, comp.shape).astype(np.float32)
    comp = np.clip(comp.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    enc.stdin.write(comp.tobytes())
    if i in (0, len(frames) // 2, len(frames) - 1):
        row = []
        for c in q:                                          # 4x zoom on each corner
            x, y = int(c[0]), int(c[1])
            x0, y0 = max(0, x - 40), max(0, y - 40)
            crop = comp[y0:y0 + 80, x0:x0 + 80]
            crop = cv2.copyMakeBorder(crop, 0, 80 - crop.shape[0], 0, 80 - crop.shape[1], cv2.BORDER_CONSTANT)
            row.append(cv2.resize(crop, (240, 240), interpolation=cv2.INTER_NEAREST))
        check.append(np.hstack(row))
enc.stdin.close()
enc.wait()
cv2.imwrite(str(ROOT / 'clips/act4-fit-check.png'), np.vstack(check))
print('wrote', OUT, f'{OUT_W}x{out_h}', len(frames), 'frames')

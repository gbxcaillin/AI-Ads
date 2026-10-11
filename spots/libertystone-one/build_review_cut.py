"""Assemble the LibertyStone picture cut (review draft, no VO/music yet).

Order: order -> overload build -> overload peak -> friction -> exhale ->
(hard reset to black) -> solution push-in -> (dissolve) -> end card with the
supplied logo animation, the USP tagline and the Australian risk line.

Silent by design for this pass: the ElevenLabs connector is erroring this
session, so the VO + music/sound layer comes next. Run from repo root:
    python3 spots/libertystone-one/build_review_cut.py
"""
import subprocess, shutil, imageio_ffmpeg
from pathlib import Path

FF = shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path('spots/libertystone-one')
CLIPS = ROOT / 'clips'
FONTS = Path('.claude/skills/ai-commercial/scripts/fonts')
M600, M500 = FONTS / 'Montserrat-600.ttf', FONTS / 'Montserrat-500.ttf'
W, H, FPS = 1280, 720, 24
TMP = ROOT / '_cut_tmp'; TMP.mkdir(exist_ok=True)

# (file, start, dur, head_fade_from_black, tail_fade_to_black)
SEGS = [
    ('act1-order.mp4',            0.0, 4.0, False, False),
    ('act2a-overload.mp4',        0.4, 4.4, False, False),
    ('act2b-overload.mp4',        1.2, 4.6, False, False),
    ('act3a-friction.mp4',        0.0, 3.4, False, False),
    ('act3b-exhale.mp4',          0.6, 2.6, False, True),   # fade to black -> reset
    ('act4-solution-pushin.mp4',  0.0, 6.0, True,  False),  # rise from black
]
GRADE = ("eq=contrast=1.05:saturation=1.06:brightness=-0.008,"
         "colorbalance=bs=0.04:bm=0.01:bh=-0.02,"
         "vignette=PI/5.2")

def run(cmd): subprocess.run(cmd, check=True)

# 1) pre-render each graded, trimmed, CFR segment
seg_files = []
for i, (f, ss, du, hf, tf) in enumerate(SEGS):
    out = TMP / f'seg{i}.mp4'
    vf = (f'scale={W}:{H}:force_original_aspect_ratio=decrease,'
          f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},{GRADE}')
    if hf: vf += ',fade=t=in:st=0:d=0.22:color=black'
    if tf: vf += f',fade=t=out:st={du-0.22:.3f}:d=0.22:color=black'
    vf += ',format=yuv420p'
    run([FF, '-y', '-loglevel', 'error', '-ss', f'{ss}', '-t', f'{du}', '-i', str(CLIPS / f),
         '-vf', vf, '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', str(out)])
    seg_files.append(out)

# 1b) a short black hold for the reset (between exhale and solution)
black = TMP / 'black.mp4'
run([FF, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'color=c=black:s={W}x{H}:r={FPS}:d=0.30',
     '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(black)])

# 2) body = hard-cut concat of seg0..seg4 + black + seg5
body = TMP / 'body.mp4'
order = seg_files[:5] + [black] + [seg_files[5]]
concat_list = TMP / 'list.txt'
concat_list.write_text(''.join(f"file '{p.resolve()}'\n" for p in order))
run([FF, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(concat_list),
     '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(body)])

# 3) end card: logo animation with the tagline + risk-line overlay faded in.
# (drawtext is absent from this ffmpeg build, so the text is a pre-rendered
# transparent PNG from render-endcard-text.mjs.)
subprocess.run(['node', str(ROOT / 'dashboard/render-endcard-text.mjs')], check=True)
endcard = TMP / 'endcard.mp4'
run([FF, '-y', '-loglevel', 'error',
     '-i', str(ROOT / 'brand/logo-animation-16x9-5s.mp4'),
     '-loop', '1', '-t', '5', '-i', str(CLIPS / 'endcard-text.png'),
     '-filter_complex',
     f'[0:v]scale={W}:{H},setsar=1,fps={FPS}[bg];'
     f'[1:v]scale={W}:{H},fps={FPS},fade=t=in:st=2.7:d=0.7:alpha=1[txt];'
     f'[bg][txt]overlay=0:0:format=auto,format=yuv420p[v]',
     '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(endcard)])

# 4) dissolve body -> endcard
def dur(p):
    import re
    err = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
bd = dur(body)
XF = 0.6
off = bd - XF
out = ROOT / 'out'; out.mkdir(exist_ok=True)
final = out / 'libertystone-review-picture.mp4'
run([FF, '-y', '-loglevel', 'error', '-i', str(body), '-i', str(endcard),
     '-filter_complex',
     f'[0:v]settb=AVTB[a];[1:v]settb=AVTB[b];[a][b]xfade=transition=fade:duration={XF}:offset={off:.3f},format=yuv420p[v]',
     '-map', '[v]', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
     '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(final)])
print('total', round(bd + dur(endcard) - XF, 2), 's ->', final)

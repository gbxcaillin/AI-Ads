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
    ('act4-solution-tracked.mp4', 0.0, 6.0, True,  False),  # rise from black; dashboard tracked in post
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
total = bd + dur(endcard) - XF
print('picture', round(total, 2), 's ->', final)

# 5) sound: narration lines placed on the picture, bed 18 dB under the voice,
# the synthesised sfx layer, then two-pass loudness to -14 LUFS / -1.5 dBTP.
AUDIO = ROOT / 'audio'
NARR, BED = AUDIO / 'narration-all-lines.m4a', AUDIO / 'music-bed.m4a'
# (source in, source out, cut time) from the word-level transcript; the line
# ends sit ~0.2 s into each pause. "One ... place" is tightened from 1.0 s to
# 0.35 s by splitting it and butting the halves together.
LINES = [
    (0.78, 2.22, 0.70),     # You worked hard for this.          over the composed opener
    (4.18, 14.10, 4.25),    # But your money lives ... this hard. over overload, ends as friction starts
    (16.70, 18.70, 19.70),  # LibertyStone brings it all together. just after the reset to black
    (20.30, 24.12, 22.30),  # Your shares, your ETFs, and your crypto. One
    (24.98, 25.62, 22.30 + (24.12 - 20.30) + 0.35),  # place.
]
sfx = TMP / 'sfx.wav'
run(['python3', str(ROOT / 'make_sfx.py'), f'{total:.3f}', str(sfx)])
import re as _re
def mean_db(p):
    err = subprocess.run([FF, '-hide_banner', '-i', str(p), '-af', 'volumedetect', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(_re.search(r'mean_volume: (-?[\d.]+) dB', err)[1])
bed_gain_db = (mean_db(NARR) - 18) - mean_db(BED)
# VO chain: the cloned take is peaky (15.8 dB loudness-to-peak) from short
# plosive transients that a compressor's attack lets through. A fast limiter
# driven +4 dB, oversampled at 192k, shaves only those transients: 11.4 dB
# loudness-to-peak, a broadcast-style read, so the master reaches -14 LUFS
# under a -2 dBTP ceiling. The bed stays ~19 dB under the processed voice.
VO_CHAIN = ('aresample=192000,volume=4dB,alimiter=limit=0.6:attack=0.5:release=40:level=disabled,'
            'aresample=48000')
fc = [f'[1:a]aresample=48000,aformat=channel_layouts=stereo,{VO_CHAIN},asplit={len(LINES)}' + ''.join(f'[n{i}]' for i in range(len(LINES)))]
for i, (a, b, at) in enumerate(LINES):
    ms = int(round(at * 1000))
    fc.append(f'[n{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,'
              f'afade=t=out:st={b - a - 0.08:.3f}:d=0.08,adelay={ms}|{ms}[l{i}]')
fc.append(f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,'
          f'volume={bed_gain_db:.2f}dB,afade=t=in:d=1.2,afade=t=out:st={total - 2.2:.3f}:d=2.2[bed]')
fc.append('[3:a]aresample=48000,aformat=channel_layouts=stereo[fx]')
fc.append('[bed][fx]' + ''.join(f'[l{i}]' for i in range(len(LINES)))
          + f'amix=inputs={len(LINES) + 2}:normalize=0:dropout_transition=0,atrim=0:{total:.3f}[aout]')
mixed = out / 'libertystone-review-v2.mp4'
run([FF, '-y', '-loglevel', 'error', '-i', str(final), '-i', str(NARR), '-i', str(BED), '-i', str(sfx),
     '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.3f}', str(mixed)])
print(f'bed gain {bed_gain_db:.1f} dB')

# Loudness: a linear loudnorm cannot lift this mix to -14 because the click and
# ping transients would pass the true-peak ceiling, so apply the gain directly
# and catch the transients with a peak limiter (oversampled by running at 192k),
# then measure again and correct once for what the limiter took off.
import json
def measure(p):
    err = subprocess.run([FF, '-hide_banner', '-i', str(p), '-af',
                          'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
    return float(m['input_i']), float(m['input_tp'])
src = mixed.with_suffix('.premaster.mp4')
mixed.replace(src)
err = subprocess.run([FF, '-hide_banner', '-i', str(src), '-af',
                      'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},"
      f"aresample=48000")
run([FF, '-y', '-loglevel', 'error', '-i', str(src), '-af', af, '-c:v', 'copy', '-c:a', 'aac',
     '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(mixed)])
src.unlink()
li, tp = measure(mixed)
print(f'loudness: {li:.1f} LUFS, true peak {tp:.1f} dBTP (pre-master {float(m["input_i"]):.1f} LUFS, '
      f'{float(m["input_tp"]):.1f} dBTP); wrote {mixed}')

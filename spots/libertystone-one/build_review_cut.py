"""Assemble the LibertyStone review cut (SMSF version, about 33 s).

Picture: order -> overload build -> overload peak -> friction -> THE SIGH
(held about 4 s, fades to black) -> reset -> solution push-in (dashboard
tracked on in post, slowed to 7 s) -> dissolve -> end card (supplied logo
animation held 0.6 s, caption "Your whole SMSF, in one place." and the risk
line).

Sound: the cloned-voice narration split into lines and placed on the picture;
her own sigh from the sigh clip, cleaned and lifted; the music bed ducked
almost to nothing around the sigh; the synthesised pings, clicks and logo
chime; then two-pass loudness to -14 LUFS / -1.5 dBTP.

Run from the repo root:
    python3 spots/libertystone-one/build_review_cut.py
"""
import json, re, subprocess, shutil
from pathlib import Path
import imageio_ffmpeg

FF = shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path('spots/libertystone-one')
CLIPS, AUDIO = ROOT / 'clips', ROOT / 'audio'
W, H, FPS = 1280, 720, 24
TMP = ROOT / '_cut_tmp'; TMP.mkdir(exist_ok=True)
OUT = ROOT / 'out'; OUT.mkdir(exist_ok=True)

# (file, start, dur, speed, head_fade_from_black, tail_fade_to_black)
# speed < 1 slows the clip (setpts); dur is the length used AFTER the change.
SEGS = [
    ('act1-order.mp4',            0.0, 4.0, 1.0,  False, False),
    ('act2a-overload.mp4',        0.4, 4.4, 1.0,  False, False),
    ('act2b-overload.mp4',        1.2, 4.6, 1.0,  False, False),
    ('act3a-friction.mp4',        0.0, 3.4, 1.0,  False, False),
    ('act3c-sigh.mp4',            0.2, 4.2, 1.0,  False, True),   # in-breath, eyes close, the sigh, a beat after
    ('act4-solution-tracked.mp4', 0.0, 7.0, 0.86, True,  False),  # rise from black; dashboard tracked in post
]
SIGH_SEG = 4
BLACK = 0.30
XF = 0.6
ENDCARD_HOLD = 1.2        # hold the settled logo after the 5 s animation (room after the 3.4 s close)
CAPTION_AT = 2.3          # end-card seconds; the wordmark lands at about 2.5
GRADE = ("eq=contrast=1.05:saturation=1.06:brightness=-0.008,"
         "colorbalance=bs=0.04:bm=0.01:bh=-0.02,"
         "vignette=PI/5.2")


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(p):
    err = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


# 1) graded, trimmed, constant-frame-rate segments
seg_files, starts, t = [], [], 0.0
for i, (f, ss, du, speed, hf, tf) in enumerate(SEGS):
    out = TMP / f'seg{i}.mp4'
    vf = (f'setpts=PTS/{speed},' if speed != 1.0 else '') + \
         (f'scale={W}:{H}:force_original_aspect_ratio=decrease,'
          f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},trim=0:{du},setpts=PTS-STARTPTS,{GRADE}')
    if hf: vf += ',fade=t=in:st=0:d=0.22:color=black'
    if tf: vf += f',fade=t=out:st={du - 0.3:.3f}:d=0.3:color=black'
    vf += ',format=yuv420p'
    run([FF, '-y', '-loglevel', 'error', '-ss', f'{ss}', '-i', str(CLIPS / f), '-vf', vf, '-an',
         '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', str(out)])
    seg_files.append(out)
    starts.append(t)
    t += du + (BLACK if i == SIGH_SEG else 0.0)
black = TMP / 'black.mp4'
run([FF, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'color=c=black:s={W}x{H}:r={FPS}:d={BLACK}',
     '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(black)])

# 2) body: hard cuts, the black reset after the sigh
body = TMP / 'body.mp4'
order = seg_files[:SIGH_SEG + 1] + [black] + seg_files[SIGH_SEG + 1:]
(TMP / 'list.txt').write_text(''.join(f"file '{p.resolve()}'\n" for p in order))
run([FF, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(TMP / 'list.txt'),
     '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(body)])

# 3) end card: logo animation, held, with the caption + risk line faded in
subprocess.run(['node', str(ROOT / 'dashboard/render-endcard-text.mjs')], check=True)
ec_len = 5.0 + ENDCARD_HOLD
endcard = TMP / 'endcard.mp4'
run([FF, '-y', '-loglevel', 'error',
     '-i', str(ROOT / 'brand/logo-animation-16x9-5s.mp4'),
     '-loop', '1', '-t', f'{ec_len}', '-i', str(CLIPS / 'endcard-text.png'),
     '-filter_complex',
     f'[0:v]scale={W}:{H},setsar=1,fps={FPS},tpad=stop_mode=clone:stop_duration={ENDCARD_HOLD + 0.1},'
     f'trim=0:{ec_len},setpts=PTS-STARTPTS[bg];'
     f'[1:v]scale={W}:{H},fps={FPS},fade=t=in:st={CAPTION_AT}:d=0.6:alpha=1[txt];'
     f'[bg][txt]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]',
     '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(endcard)])

# 4) dissolve body -> end card
bd = dur(body)
ec_start = bd - XF
picture = OUT / 'libertystone-review-picture.mp4'
run([FF, '-y', '-loglevel', 'error', '-i', str(body), '-i', str(endcard), '-filter_complex',
     f'[0:v]settb=AVTB[a];[1:v]settb=AVTB[b];[a][b]xfade=transition=fade:duration={XF}:offset={ec_start:.3f},format=yuv420p[v]',
     '-map', '[v]', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
     '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(picture)])
total = dur(picture)
sigh_at = starts[SIGH_SEG]
print(f'picture {total:.2f}s; sigh shot at {sigh_at:.2f}s; end card at {ec_start:.2f}s')

# 5) sound
NARR, BED = AUDIO / 'narration-smsf.m4a', AUDIO / 'music-bed.m4a'
# The closing line is a separate short take: the main take read the
# abbreviation as four even letters; the client wants "S M", a quarter-beat
# pause, "S F". audio/close-take.json names the take and its in/out points,
# chosen with check_smsf.py.
_ct = json.loads((AUDIO / 'close-take.json').read_text())
CLOSE_TAKE, CLOSE_IN, CLOSE_OUT = AUDIO / _ct['take'], _ct['in'], _ct['out']
SRC_GAIN = {str(CLOSE_TAKE): _ct.get('gain_db', 0.0)}   # level-match the re-take to the main take
# (source in, source out, cut time[, source file]) from the word-level
# transcript and the pauses; each line ends ~0.2 s into its pause.
LINES = [
    (0.58, 3.37, 0.60),               # You set up your own super fund to take control.
    (4.62, 13.90, 4.30),              # But now it's spread everywhere ... Statements for the auditor.
    (15.35, 20.50, sigh_at + 4.35),   # LibertyStone is the investment platform built for self-managed super funds.  (on the reset)
    (21.49, 24.20, ec_start - 0.90),  # Shares, ETFs and crypto.   (end of the solution, into the dissolve)
    (CLOSE_IN, CLOSE_OUT, ec_start + 2.25, CLOSE_TAKE),  # Your whole S M, S F, in one place.  (re-take, with the caption)
]
sfx = TMP / 'sfx.wav'
run(['python3', str(ROOT / 'make_sfx.py'), f'{total:.3f}', str(sfx), f'{ec_start + 1.2:.2f}'])


def mean_db(p):
    err = subprocess.run([FF, '-hide_banner', '-i', str(p), '-af', 'volumedetect', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.search(r'mean_volume: (-?[\d.]+) dB', err)[1])


bed_gain_db = (mean_db(NARR) - 18) - mean_db(BED)
bed_tempo = min(1.0, dur(BED) / total)                # stretch the one take, never loop
# VO: a fast limiter driven +4 dB (oversampled) shaves the plosive transients.
VO_CHAIN = 'aresample=192000,volume=4dB,alimiter=limit=0.6:attack=0.5:release=40:level=disabled,aresample=48000'
# The sigh: her own breath from the clip, hiss removed, room tone between the
# in-breath and the sigh gated away, lifted so it carries over the near-silence.
SIGH_SRC, SIGH_DUR, SIGH_GAIN = SEGS[SIGH_SEG][1], SEGS[SIGH_SEG][2], 6.0
SIGH_CHAIN = ('highpass=f=90,afftdn=nr=18:nf=-38:tn=1,'
              'agate=threshold=0.03:ratio=6:attack=5:release=250,'
              f'volume={SIGH_GAIN}dB')
# Bed ducks ~18 dB from just before the sigh shot until the solution is up.
d0, d1 = sigh_at - 0.25, sigh_at + SIGH_DUR + BLACK + 0.3
duck = f"volume='1-0.88*min(1,max(0,(t-{d0:.2f})/0.3))*min(1,max(0,({d1 + 0.8:.2f}-t)/0.8))':eval=frame"

# narration sources: the main take is input 1; any re-take is added after the sigh clip
srcs = [NARR] + sorted({str(l[3]) for l in LINES if len(l) > 3 and str(l[3]) != str(NARR)})
src_idx = {str(NARR): 1, **{s: 5 + k for k, s in enumerate(srcs[1:])}}
users = {s: [i for i, l in enumerate(LINES) if str(l[3] if len(l) > 3 else NARR) == s] for s in map(str, srcs)}
fc = []
for s_, idxs in users.items():
    fc.append(f'[{src_idx[s_]}:a]aresample=48000,aformat=channel_layouts=stereo,volume={SRC_GAIN.get(s_, 0.0)}dB,{VO_CHAIN},asplit={len(idxs)}'
              + ''.join(f'[n{i}]' for i in idxs))
for i, line in enumerate(LINES):
    a, b, at = line[:3]
    ms = int(round(at * 1000))
    fc.append(f'[n{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,'
              f'afade=t=out:st={b - a - 0.08:.3f}:d=0.08,adelay={ms}|{ms}[l{i}]')
fc.append(f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atempo={bed_tempo:.5f},'
          f'atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={bed_gain_db:.2f}dB,{duck},'
          f'afade=t=in:d=1.2,afade=t=out:st={total - 2.2:.3f}:d=2.2[bed]')
fc.append('[3:a]aresample=48000,aformat=channel_layouts=stereo[fx]')
sms = int(round(sigh_at * 1000))
fc.append(f'[4:a]aresample=48000,aformat=channel_layouts=stereo,atrim={SIGH_SRC}:{SIGH_SRC + SIGH_DUR},'
          f'asetpts=PTS-STARTPTS,{SIGH_CHAIN},afade=t=in:d=0.05,afade=t=out:st={SIGH_DUR - 0.3:.2f}:d=0.3,'
          f'adelay={sms}|{sms}[sigh]')
fc.append('[bed][fx][sigh]' + ''.join(f'[l{i}]' for i in range(len(LINES)))
          + f'amix=inputs={len(LINES) + 3}:normalize=0:dropout_transition=0,atrim=0:{total:.3f}[aout]')
mixed = OUT / 'libertystone-review-v3.mp4'
pre = mixed.with_suffix('.premaster.mp4')
run([FF, '-y', '-loglevel', 'error', '-i', str(picture), '-i', str(NARR), '-i', str(BED), '-i', str(sfx),
     '-i', str(CLIPS / SEGS[SIGH_SEG][0]), *sum((['-i', s_] for s_ in srcs[1:]), []),
     '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.3f}', str(pre)])
print(f'bed gain {bed_gain_db:.1f} dB, tempo {bed_tempo:.3f}, ducked {d0:.2f}-{d1:.2f}s')

# 6) two-pass loudness, house web target
def loud_json(p):
    err = subprocess.run([FF, '-hide_banner', '-i', str(p), '-af',
                          'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return json.loads(err[err.rfind('{'):err.rfind('}') + 1])
m = loud_json(pre)
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
run([FF, '-y', '-loglevel', 'error', '-i', str(pre), '-af', af, '-c:v', 'copy', '-c:a', 'aac',
     '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(mixed)])
pre.unlink()
r = loud_json(mixed)
print(f"loudness: {float(r['input_i']):.1f} LUFS, true peak {float(r['input_tp']):.1f} dBTP; wrote {mixed}")

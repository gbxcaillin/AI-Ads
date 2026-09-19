"""Assemble the six commercial clips into one cut with a continuous soundtrack.

Line boundaries come from LINES when present (write it from a word-level transcript,
for example faster-whisper with word_timestamps=True); otherwise the pauses in the
narration are used, which only works when the reader leaves a clear gap between lines.

Usage (from the repo root, with the clips in one folder):
    python3 scripts/stitch-commercial.py <clips-dir> <output.mp4>

Picture: each clip is muted and trimmed to fit its narration line snugly
(LEAD before the line, CLIP_TAIL after it), then dissolves into the next over
XFADE seconds (no dip to black). This keeps the ad tight instead of holding long
silent tails. The final clip keeps its full length so the end card can resolve.

Sound: one narration take (NARRATION, a silent-studio carrier that reads all six
lines in order) is split into lines at the pauses, and line i is placed LEAD
seconds after clip i starts (a J-cut: the line begins while the previous picture is
still dissolving out). One instrumental bed (BED) runs under the whole cut at
BED_UNDER_DB below the narration (broadcast convention 18 to 20), stretched
slightly to fill the length rather than looped, and fades at the end. The clips'
own audio is not used, so nothing jumps at the joins. The finished file is then
loudness-normalised in two passes to LOUDNESS=web (-14 LUFS, -1 dBTP) or
broadcast (-24 LKFS, -2 dBTP).

Requires ffmpeg on PATH or the imageio-ffmpeg package (pip install imageio-ffmpeg).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CLIPS = [
    'clip1-clearer-picture-7s.mp4',
    'clip2-run-sharper-7s-v2.mp4',
    'clip3-ai-7s-v6.mp4',
    'clip4-teaching-7s-v3.mp4',
    'clip5-tools-screencap-7s.mp4',
    'clip6-endcard-picture.mp4',
]
NARRATION = os.environ.get('NARRATION', 'narration-all-lines.m4a')   # one-take read of the six lines (audio or video file)
LINES = 'narration-lines.txt'           # optional: one 'start<TAB>end' per line, in seconds, from a word-level transcript
BED = os.environ.get('BED', 'music-bed.m4a')   # instrumental bed (any audio or video file), no voice
XFADE = 0.7        # seconds each dissolve takes
LEAD = 0.35        # seconds after a clip starts before its line begins
CLIP_TAIL = 0.55   # seconds of picture after the line finishes, before the dissolve starts
MIN_CLIP = 3.0     # never trim a clip shorter than this
CLIP_EXTRA = {2: 0.5}   # extra seconds of screen time for specific clips (0-based index); clip 3 gets +0.5s
WHITE_FADES = {5}  # 1-based clip numbers whose dissolve INTO them fades through white instead of a plain crossfade
BED_UNDER_DB = float(os.environ.get('BED_UNDER_DB', '18'))   # bed sits this far under the narration; 18 to 20 is the broadcast convention, under 15 masks speech on phones
LOUDNESS = os.environ.get('LOUDNESS', 'web')   # 'web' (-14 LUFS, -1 dBTP: YouTube and most platforms), 'broadcast' (-24 LKFS, -2 dBTP: CALM, OP-59) or 'none'
LOUDNESS_TARGETS = {'web': (-14.0, -1.5), 'broadcast': (-24.0, -2.5)}   # half a dB of true-peak headroom below the platform ceiling, because the AAC encode overshoots slightly
VO_GAIN = 1.0
SIZE = (1280, 720)
LINE_GAP = 0.9     # pauses shorter than this are inside a line, not between lines
SILENCE_DB = -38


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def mean_db(ff, path):
    err = subprocess.run([ff, '-hide_banner', '-i', str(path), '-af', 'volumedetect', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.search(r'mean_volume: (-?[\d.]+) dB', err)[1])


def duration(ff, path):
    err = subprocess.run([ff, '-i', str(path)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def speech_segments(ff, path, count):
    """Split a narration carrier into `count` spoken lines using the pauses between them."""
    err = subprocess.run([ff, '-hide_banner', '-i', str(path), '-af',
                          f'highpass=f=120,silencedetect=n={SILENCE_DB}dB:d=0.25', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    total = duration(ff, path)
    # speech runs between silences
    runs, t = [], 0.0
    for s, e in zip(starts, ends):
        if s > t:
            runs.append([t, s])
        t = e
    if t < total - 0.05:
        runs.append([t, total])
    # merge runs separated by short pauses until we have `count` lines
    def gaps(r):
        return [r[i + 1][0] - r[i][1] for i in range(len(r) - 1)]
    while len(runs) > count:
        g = gaps(runs)
        i = g.index(min(g))
        runs[i] = [runs[i][0], runs[i + 1][1]]
        del runs[i + 1]
    if len(runs) != count:
        sys.exit(f'found {len(runs)} spoken lines in {path}, expected {count}: {runs}')
    return [(max(0.0, a - 0.08), min(total, b + 0.15)) for a, b in runs]


def main(clips_dir, out):
    ff = ffmpeg()
    d = Path(clips_dir)
    vids = [d / c for c in CLIPS]
    actual = [duration(ff, v) for v in vids]
    if (d / LINES).exists():
        lines = [tuple(float(x) for x in l.split()[:2]) for l in (d / LINES).read_text().splitlines() if l.strip()]
        if len(lines) != len(vids):
            sys.exit(f'{LINES} has {len(lines)} lines, expected {len(vids)}')
    else:
        lines = speech_segments(ff, d / NARRATION, len(vids))
    line_len = [b - a for a, b in lines]
    last = len(vids) - 1
    w, h = SIZE
    # `used` is the unique screen time each clip gets (LEAD before the line,
    # CLIP_TAIL after). `shown` adds XFADE of real footage that plays during the
    # dissolve into the next clip. The last clip keeps its full length so the end
    # card can resolve. Every clip is pre-rendered to a clean, constant-frame-rate
    # file of an exact known length: doing the trim inside the big xfade graph
    # produced variable frame rate and a broken chain, so we stage it instead.
    tmp = Path(clips_dir) / '_stitch_tmp'
    tmp.mkdir(exist_ok=True)
    used, shown, seg = [], [], []
    for i in range(len(vids)):
        extra = CLIP_EXTRA.get(i, 0.0)
        u = actual[i] if i == last else max(MIN_CLIP, min(LEAD + line_len[i] + CLIP_TAIL + extra, actual[i]))
        s = actual[i] if i == last else min(actual[i], u + XFADE)
        used.append(u)
        shown.append(s)
        out_i = tmp / f'seg{i}.mp4'
        seg.append(out_i)
        vf = (f'scale={w}:{h}:force_original_aspect_ratio=decrease,'
              f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,format=yuv420p,'
              f'trim=0:{s:.3f},setpts=PTS-STARTPTS')
        subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(vids[i]), '-vf', vf,
                        '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                        '-pix_fmt', 'yuv420p', str(out_i)], check=True)
    # timeline: each clip advances the running length by (shown - XFADE)
    starts = [0.0]
    out_len = shown[0]
    for i in range(1, len(vids)):
        starts.append(out_len - XFADE)
        out_len = starts[i] + shown[i]
    total = out_len
    for i, (a, b) in enumerate(lines):
        print(f'line {i + 1}: {b - a:.1f}s speech, clip shown {shown[i]:.1f}s, line at {starts[i] + LEAD:.2f}s')
    bed_len = duration(ff, d / BED)
    vo_db = mean_db(ff, d / NARRATION)
    bed_gain = 10 ** ((vo_db - BED_UNDER_DB - mean_db(ff, d / BED)) / 20)
    print(f'narration {vo_db:.1f} dB mean; bed set {BED_UNDER_DB:.0f} dB under (gain x{bed_gain:.2f}); total {total:.1f}s')

    inputs = []
    for s in seg:
        inputs += ['-i', str(s)]
    inputs += ['-i', str(d / NARRATION), '-i', str(d / BED)]
    n_idx, b_idx = len(vids), len(vids) + 1
    fc = []
    # picture: the segments are already clean and CFR, so just settb then dissolve
    for i in range(len(vids)):
        fc.append(f'[{i}:v]settb=AVTB[v{i}]')
    pv = 'v0'
    for i in range(1, len(vids)):
        kind = 'fadewhite' if (i + 1) in WHITE_FADES else 'fade'
        fc.append(f'[{pv}][v{i}]xfade=transition={kind}:duration={XFADE}:offset={starts[i]:.3f}[xv{i}]')
        pv = f'xv{i}'
    # narration lines
    fc.append(f'[{n_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(vids)}'
              + ''.join(f'[n{i}]' for i in range(len(vids))))
    mix_in = []
    for i, (a, b) in enumerate(lines):
        at = int(round((starts[i] + LEAD) * 1000))
        fc.append(f'[n{i}]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={b - a - 0.12:.3f}:d=0.12,'
                  f'volume={VO_GAIN},adelay={at}|{at}[l{i}]')
        mix_in.append(f'[l{i}]')
    # bed: cover the whole cut from the single take. Looping a short bed leaves a
    # crossfade seam that dips out (audible in a voice gap), so instead slow the
    # bed very slightly to fill the length: a drone stretched a little is
    # imperceptible and has no seam. atempo handles 0.5x-2.0x; chain it past that.
    factor = bed_len / total if bed_len < total else 1.0
    tempo = ''
    if bed_len < total - 0.05:
        f = factor
        steps = []
        while f < 0.5:
            steps.append(0.5)
            f /= 0.5
        steps.append(f)
        tempo = ''.join(f'atempo={x:.5f},' for x in steps)
    fc.append(f'[{b_idx}:a]aresample=48000,aformat=channel_layouts=stereo,{tempo}'
              f'atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={bed_gain:.3f},'
              f'afade=t=in:d=1.0,afade=t=out:st={max(0.0, total - 2.5):.3f}:d=2.5[bed]')
    fc.append(''.join(mix_in) + f'[bed]amix=inputs={len(mix_in) + 1}:normalize=0:dropout_transition=0[aout]')

    cmd = [ff, '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
           '-map', f'[{pv}]', '-map', '[aout]', '-t', f'{total:.3f}',
           '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)
    for s in seg:
        s.unlink(missing_ok=True)
    tmp.rmdir()
    if LOUDNESS in LOUDNESS_TARGETS:
        normalise_loudness(ff, Path(out), *LOUDNESS_TARGETS[LOUDNESS])
    print('wrote', out, 'about', round(total, 1), 'seconds')


def normalise_loudness(ff, path, target_i, target_tp):
    """Two-pass EBU R128 loudnorm on the finished file: measure, then apply with the
    measured values so the correction is a linear gain (no pumping). Video is copied."""
    import json
    err = subprocess.run([ff, '-hide_banner', '-i', str(path), '-af',
                          f'loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
    af = (f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true:print_format=summary")
    tmp = path.with_suffix('.loud.mp4')
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(path), '-af', af, '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(tmp)], check=True)
    tmp.replace(path)
    print(f'loudness: measured {float(m["input_i"]):.1f} LUFS, {float(m["input_tp"]):.1f} dBTP; normalised to {target_i} LUFS, {target_tp} dBTP')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

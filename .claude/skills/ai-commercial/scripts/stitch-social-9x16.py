"""Cut one short 9:16 social piece: N picture clips, one narration line across
them, a brand close (end card with its own line), one music bed, captions later.

Usage:
    python3 scripts/stitch-social-9x16.py <piece.json> <out.mp4>

piece.json (paths relative to the json folder, or to its optional "base"):
{
  "size": [1080, 1920], "fps": 24, "xfade": 0.7,
  "clips": [{"file": "clips/A1.mp4"}, {"file": "clips/A2.mp4", "join": "fadewhite"}],
  "tail": {"file": "../gbx-commercial/captures/clip6-endcard-9x16.mp4", "length": 8.0},
  "narration": "../gbx-commercial/audio/narration-all-lines.m4a",
  "bed": "../gbx-commercial/audio/music-bed.m4a", "bed_under_db": 18,
  "line":  {"start": 0.0, "end": 3.9, "split": 2.34, "at": 0.6},
  "close": {"start": 22.94, "end": 29.9, "at_offset": 0.85},
  "loudness": "web"
}

Timing: the line starts `at` seconds into the piece. Clip 1 is trimmed so the
middle of its dissolve lands on `split` (the first word of the line's second
sentence), never shorter than min_clip (3.0 s); every other clip plays full
length; the tail plays `length` seconds and carries the close line from
`at_offset` after it starts. The bed is trimmed to the piece (not stretched) and
fades out over the last 2.5 s. Loudness is normalised as in stitch-commercial.py.
Writes <out>.timing.json with the clip starts and the two line placements so the
captions script can shift word timings from the take onto the cut.
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_CLIP = 3.0


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(ff, path):
    err = subprocess.run([ff, '-i', str(path)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def mean_db(ff, path):
    err = subprocess.run([ff, '-hide_banner', '-i', str(path), '-af', 'volumedetect', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.search(r'mean_volume: (-?[\d.]+) dB', err)[1])


def main(spec_path, out):
    spec = json.loads(Path(spec_path).read_text())
    base = (Path(spec_path).resolve().parent / spec.get('base', '.')).resolve()   # paths in the spec are relative to this
    ff = ffmpeg()
    w, h = spec.get('size', [1080, 1920])
    fps = spec.get('fps', 24)
    xf = spec.get('xfade', 0.7)
    line, close = spec['line'], spec['close']
    files = [base / c['file'] for c in spec['clips']] + [base / spec['tail']['file']]
    joins = [c.get('join', 'fade') for c in spec['clips'][1:]] + [spec['tail'].get('join', 'fade')]
    actual = [duration(ff, f) for f in files]
    # unique screen time per clip (clip 1 trimmed to the split; last is the tail)
    shown = list(actual)
    shown[-1] = min(actual[-1], spec['tail'].get('length', actual[-1]))
    want = line['at'] + (line['split'] - line['start']) + xf / 2
    shown[0] = max(MIN_CLIP, min(actual[0], want))
    starts = [0.0]
    for i in range(1, len(shown)):
        starts.append(starts[-1] + shown[i - 1] - xf)
    total = starts[-1] + shown[-1]
    tail_at = starts[-1]
    close_at = tail_at + close['at_offset']
    print(f'clips shown: {[round(s, 2) for s in shown]}, starts {[round(s, 2) for s in starts]}, total {total:.2f}s')
    print(f'line at {line["at"]:.2f}s (split lands at {line["at"] + line["split"] - line["start"]:.2f}s, dissolve mid at {starts[1] + xf / 2:.2f}s); close at {close_at:.2f}s')

    tmp = Path(tempfile.mkdtemp())
    staged = []
    for i, (f, s) in enumerate(zip(files, shown)):
        p = tmp / f'c{i}.mp4'
        vf = (f'scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},'
              f'setsar=1,fps={fps},format=yuv420p')
        subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(f), '-t', f'{s:.3f}', '-an', '-vf', vf,
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', str(p)], check=True)
        staged.append(p)
    inputs = []
    for p in staged:
        inputs += ['-i', str(p)]
    n_idx, b_idx = len(staged), len(staged) + 1
    inputs += ['-i', str(base / spec['narration']), '-i', str(base / spec['bed'])]
    fc = []
    pv = '0:v'
    for i in range(1, len(staged)):
        fc.append(f'[{pv}][{i}:v]xfade=transition={joins[i - 1]}:duration={xf}:offset={starts[i]:.3f}[xv{i}]')
        pv = f'xv{i}'
    fc.append(f'[{n_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[n0][n1]')
    mix = []
    for j, (seg, at) in enumerate(((line, line['at']), (close, close_at))):
        a, b = seg['start'], seg['end']
        ms = int(round(at * 1000))
        fc.append(f'[n{j}]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,'
                  f'afade=t=out:st={b - a - 0.12:.3f}:d=0.12,adelay={ms}|{ms}[l{j}]')
        mix.append(f'[l{j}]')
    bed_gain = (mean_db(ff, base / spec['narration']) - spec.get('bed_under_db', 18)) - mean_db(ff, base / spec['bed'])
    fc.append(f'[{b_idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,'
              f'volume={bed_gain:.2f}dB,afade=t=in:d=1.0,afade=t=out:st={max(0.0, total - 2.5):.3f}:d=2.5[bed]')
    fc.append('[bed]' + ''.join(mix) + f'amix=inputs={len(mix) + 1}:normalize=0:dropout_transition=0[aout]')
    subprocess.run([ff, '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
                    '-map', f'[{pv}]', '-map', '[aout]', '-t', f'{total:.3f}',
                    '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    loud = spec.get('loudness', 'web')
    if loud in ('web', 'broadcast'):
        sp = importlib.util.spec_from_file_location('stitch_commercial', HERE / 'stitch-commercial.py')
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        mod.normalise_loudness(ff, Path(out), *mod.LOUDNESS_TARGETS[loud])
    Path(str(out) + '.timing.json').write_text(json.dumps({
        'starts': starts, 'shown': shown, 'total': total, 'line_at': line['at'], 'close_at': close_at,
        'tail_at': tail_at}, indent=1))
    print('wrote', out, 'about', round(total, 1), 'seconds')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

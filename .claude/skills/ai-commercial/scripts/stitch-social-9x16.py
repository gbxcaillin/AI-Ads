"""Cut one short 9:16 social piece: N picture clips, one narration line across
them, a brand close over the end card, one music bed. Captions are burned in
afterwards by captions-9x16.py.

Usage:
    python3 scripts/stitch-social-9x16.py <piece.json> <out.mp4>

piece.json (paths relative to the json folder, or to its optional "base"):
{
  "size": [1080, 1920], "fps": 24, "xfade": 0.7,
  "trim_first": false,            # true trims clip 1 so its dissolve lands on `line.split`;
                                  # false plays every picture clip full (right for a long line)
  "clips": [{"file": "clips/A1.mp4"}, {"file": "clips/A2.mp4", "join": "fadewhite"}],
  "tail": {"file": "../gbx-commercial/captures/clip6-endcard-9x16.mp4", "length": 8.0},
  "narration": "audio/carrier1.m4a",        # the line comes from here
  "close_narration": "audio/carrier1.m4a",  # optional: the close comes from here (defaults to narration)
  "bed": "../gbx-commercial/audio/music-bed.m4a", "bed_under_db": 18,
  "line":  {"start": 0.0, "end": 9.8, "split": 7.0, "at": 0.6},
  "close": {"start": 24.7, "end": 27.3, "at_offset": 0.85, "gap": 0.6},
  "loudness": "web"
}

Timing: the line starts `at` seconds into the piece. With trim_first the first
clip is trimmed so its dissolve lands on `line.split`; otherwise every clip plays
full. The tail (end card) plays `tail.length` seconds and carries the close from
max(tail_start + close.at_offset, line_end + close.gap), so the close never steps
on the tail of a long line. The bed is trimmed to the piece and fades out over the
last 2.5 s. Loudness is normalised as in stitch-commercial.py. Writes
<out>.timing.json with the clip starts and the two line placements so the captions
script can shift the take's word timings onto the cut.
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
    base = (Path(spec_path).resolve().parent / spec.get('base', '.')).resolve()
    ff = ffmpeg()
    w, h = spec.get('size', [1080, 1920])
    fps = spec.get('fps', 24)
    xf = spec.get('xfade', 0.7)
    line, close = spec['line'], spec['close']
    files = [base / c['file'] for c in spec['clips']] + [base / spec['tail']['file']]
    joins = [c.get('join', 'fade') for c in spec['clips'][1:]] + [spec['tail'].get('join', 'fade')]
    actual = [duration(ff, f) for f in files]
    shown = list(actual)
    shown[-1] = min(actual[-1], spec['tail'].get('length', actual[-1]))
    if spec.get('trim_first', True):
        want = line['at'] + (line['split'] - line['start']) + xf / 2
        shown[0] = max(MIN_CLIP, min(actual[0], want))
    starts = [0.0]
    for i in range(1, len(shown)):
        starts.append(starts[-1] + shown[i - 1] - xf)
    total = starts[-1] + shown[-1]
    tail_at = starts[-1]
    line_at = line['at']
    line_dur = line['end'] - line['start']
    close_at = max(tail_at + close['at_offset'], line_at + line_dur + close.get('gap', 0.6))
    print(f'clips shown {[round(s, 2) for s in shown]}, starts {[round(s, 2) for s in starts]}, total {total:.2f}s')
    print(f'line at {line_at:.2f}s runs to {line_at + line_dur:.2f}s; card at {tail_at:.2f}s; close at {close_at:.2f}s')

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
    narr = base / spec['narration']
    closesrc = base / spec.get('close_narration', spec['narration'])
    n_idx = len(staged)
    inputs += ['-i', str(narr)]
    if closesrc != narr:
        c_idx = len(staged) + 1
        b_idx = len(staged) + 2
        inputs += ['-i', str(closesrc), '-i', str(base / spec['bed'])]
        line_src, close_src = f'{n_idx}:a', f'{c_idx}:a'
    else:
        b_idx = len(staged) + 1
        inputs += ['-i', str(base / spec['bed'])]
        line_src = close_src = None  # via asplit below
    fc = []
    pv = '0:v'
    for i in range(1, len(staged)):
        fc.append(f'[{pv}][{i}:v]xfade=transition={joins[i - 1]}:duration={xf}:offset={starts[i]:.3f}[xv{i}]')
        pv = f'xv{i}'
    if line_src is None:
        fc.append(f'[{n_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[n0][n1]')
        line_src, close_src = 'n0', 'n1'
    else:
        fc.append(f'[{line_src}]aresample=48000,aformat=channel_layouts=stereo[n0]')
        fc.append(f'[{close_src}]aresample=48000,aformat=channel_layouts=stereo[n1]')
        line_src, close_src = 'n0', 'n1'
    mix = []
    for tag, (seg, at) in (('l0', (line, line_at)), ('l1', (close, close_at))):
        src = 'n0' if tag == 'l0' else 'n1'
        a, b = seg['start'], seg['end']
        ms = int(round(at * 1000))
        fc.append(f'[{src}]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,'
                  f'afade=t=out:st={b - a - 0.12:.3f}:d=0.12,adelay={ms}|{ms}[{tag}]')
        mix.append(f'[{tag}]')
    bed_gain = (mean_db(ff, narr) - spec.get('bed_under_db', 18)) - mean_db(ff, base / spec['bed'])
    fc.append(f'[{b_idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,'
              f'volume={bed_gain:.2f}dB,afade=t=in:d=1.0,afade=t=out:st={max(0.0, total - 2.5):.3f}:d=2.5[bed]')
    fc.append('[bed]' + ''.join(mix) + f'amix=inputs={len(mix) + 1}:normalize=0:dropout_transition=0[aout]')
    subprocess.run([ff, '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
                    '-map', f'[{pv}]', '-map', '[aout]', '-t', f'{total:.3f}',
                    '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-ar', '48000', '-b:a', '160k', '-movflags', '+faststart', str(out)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    loud = spec.get('loudness', 'web')
    if loud in ('web', 'broadcast'):
        sp = importlib.util.spec_from_file_location('stitch_commercial', HERE / 'stitch-commercial.py')
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        mod.normalise_loudness(ff, Path(out), *mod.LOUDNESS_TARGETS[loud])
    Path(str(out) + '.timing.json').write_text(json.dumps({
        'starts': starts, 'shown': shown, 'total': total, 'line_at': line_at,
        'close_at': close_at, 'tail_at': tail_at}, indent=1))
    print('wrote', out, 'about', round(total, 1), 'seconds')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

"""Reframe a finished 16:9 cut to 9:16 for social, keeping its audio.

Usage:
    python3 scripts/reframe-9x16.py <cut16x9.mp4> <spec.json> <out.mp4>

The picture is cropped to a 9:16 column of the source (full height, ih*9/16 wide)
and scaled to 1080x1920. Where the column sits is set per clip in the spec, in
source pixels of the column's left edge; between two segments the offset eases
linearly, which is how a change of framing hides inside a dissolve. Anything
that cannot survive a crop (a web page, the end card) is replaced from `at`
onward by natively recorded portrait clips, staged to constant frame rate and
dissolved together, then overlaid on the cropped base. Audio is copied from the
source, so timing and loudness are unchanged.

Spec (all times in seconds of the source cut):
{
  "pans": [                                   # optional; default is the centre column
    {"from": 0.0,  "to": 4.7,  "x": [500, 420]},   # left edge pans 500 to 420 across the segment
    {"from": 5.4,  "to": 11.1, "x": [540, 540]}    # gap 4.7 to 5.4 eases 420 to 540 (the dissolve)
  ],
  "tail": {                                   # optional
    "at": 23.65,                              # where the portrait clips take over
    "xfade": 0.7,                             # dissolve between the tail clips
    "clips": [
      {"file": "clips/clip5-tools-9x16.mp4", "fade_from_white": 0.35, "length": 5.55},
      {"file": "clips/clip6-endcard-9x16.mp4", "pad": 0.4}
    ]
  }
}
`length` trims a tail clip to the unique time it should hold before its dissolve
starts (so the next clip begins at at + length); `pad` clones the last frame so
the final clip reaches the end of the cut. Requires ffmpeg on PATH or imageio-ffmpeg.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

OUT_W, OUT_H = 1080, 1920


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(ff, path):
    err = subprocess.run([ff, '-i', str(path)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    w, h = map(int, re.search(r'Video:.*?(\d{3,5})x(\d{3,5})', err).groups())
    fps = float(re.search(r'([\d.]+) fps', err)[1])
    return dur, w, h, fps


def x_expression(pans, centre):
    """Nested if() giving the crop's left edge as a function of t."""
    if not pans:
        return str(centre)
    pans = sorted(pans, key=lambda p: p['from'])
    parts = []
    prev = None
    for p in pans:
        a, b = p['from'], p['to']
        x0, x1 = p['x']
        if prev is not None and a > prev[0]:   # ease across the gap (a dissolve)
            pa, px = prev
            parts.append((a, f'{px}+({x0}-{px})*(t-{pa})/{a - pa}'))
        parts.append((b, f'{x0}+({x1}-{x0})*(t-{a})/{b - a}' if b > a else str(x0)))
        prev = (b, x1)
    expr = str(prev[1])
    for end, e in reversed(parts):
        expr = f'if(lt(t,{end}),{e},{expr})'
    return expr


def main(src, spec_path, out):
    ff = ffmpeg()
    spec = json.loads(Path(spec_path).read_text())
    base_dir = Path(spec_path).parent
    dur, w, h, fps = probe(ff, src)
    cw = int(round(h * 9 / 16))
    centre = (w - cw) // 2
    xexpr = x_expression(spec.get('pans', []), centre)
    print(f'source {w}x{h} {fps:g} fps {dur:.2f}s; crop {cw}x{h}; x = {xexpr}')

    tmp = Path(out).parent / '_reframe_tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    tail_file = None
    tail = spec.get('tail')
    if tail:
        xf = tail.get('xfade', 0.7)
        staged = []
        for i, c in enumerate(tail['clips']):
            f = base_dir / c['file'] if not Path(c['file']).is_absolute() else Path(c['file'])
            vf = [f'fps={fps:g}', f'scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase', f'crop={OUT_W}:{OUT_H}']
            if c.get('fade_from_white'):
                vf.append(f"fade=t=in:st=0:d={c['fade_from_white']}:color=white")
            if c.get('pad'):
                vf.append(f"tpad=stop_mode=clone:stop_duration={c['pad']}")
            if c.get('length'):
                vf.append(f"trim=0:{c['length'] + xf:.3f}")
            vf += ['setpts=PTS-STARTPTS', 'format=yuv420p']
            s = tmp / f'tail{i}.mp4'
            subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(f), '-vf', ','.join(vf), '-an',
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', str(s)], check=True)
            staged.append(s)
        # dissolve the staged clips in sequence; each clip's unique time is its length minus one dissolve
        cur = staged[0]
        offset = probe(ff, cur)[0] - xf
        for i, nxt in enumerate(staged[1:], 1):
            joined = tmp / f'join{i}.mp4'
            subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(cur), '-i', str(nxt), '-filter_complex',
                            f'[0:v]settb=AVTB[a];[1:v]settb=AVTB[b];[a][b]xfade=transition=fade:duration={xf}:offset={offset:.3f},format=yuv420p',
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', str(joined)], check=True)
            cur = joined
            offset = probe(ff, cur)[0] - xf
        tail_file = cur

    fc = [f"[0:v]crop={cw}:{h}:'{xexpr}':0,scale={OUT_W}:{OUT_H}:flags=lanczos,setsar=1[base]"]
    inputs = ['-i', str(src)]
    last = 'base'
    if tail_file:
        inputs += ['-i', str(tail_file)]
        at = tail['at']
        fc.append(f'[1:v]setpts=PTS+{at}/TB[tail]')
        fc.append(f"[base][tail]overlay=0:0:eof_action=pass:enable='gte(t,{at})'[ov]")
        last = 'ov'
    fc.append(f'[{last}]format=yuv420p[v]')
    subprocess.run([ff, '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
                    '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
                    '-c:a', 'copy', '-movflags', '+faststart', '-t', f'{dur:.3f}', str(out)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('wrote', out, f'{OUT_W}x{OUT_H}, {dur:.1f}s, audio copied from the source')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

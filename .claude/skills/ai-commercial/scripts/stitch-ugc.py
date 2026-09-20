"""Assemble UGC-style talking clips into one 9:16 reel with hard cuts and each clip's own dialogue.

Usage:
    python3 scripts/stitch-ugc.py <spec.json> <out.mp4>

spec.json:
{
  "size": [1080, 1920], "fps": 25,
  "title_style": {"font": "Montserrat", "size": 64},         # optional
  "sections": [
    {"title": "Priya, accounting practice",                    # optional 2 s title card before the section
     "clips": ["clips/priya-1.mp4", "clips/priya-2.mp4", ...]}
  ],
  "tail_pad": 0.35,        # seconds kept after the last speech in each clip (the rest is cut)
  "head_pad": 0.15,        # seconds kept before the first speech
  "gap_black": 0.4,        # black between sections, seconds (0 for none)
  "loudness": "web"        # web (-14 LUFS, -1.5 dBTP target), broadcast or none
}

Why: a narrated spot mutes its clips and lays one voice over them; UGC is the
opposite. Each clip carries its own dialogue and the cuts are jump cuts, so the
job is to trim the dead air at both ends of every take (generated talking clips
start late and hold after the last word), match every clip to one size and frame
rate, butt them together, and normalise the whole reel once. Title cards are
drawn with libass because this ffmpeg build has no drawtext.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FONT_DIR = Path(__file__).parent / 'fonts'


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(ff, path):
    err = subprocess.run([ff, '-i', str(path)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def speech_bounds(ff, path):
    """First and last moment of speech in the clip, from silencedetect on the voice band."""
    err = subprocess.run([ff, '-hide_banner', '-i', str(path), '-af', 'highpass=f=150,silencedetect=n=-35dB:d=0.3',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    total = duration(ff, path)
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    first = ends[0] if starts and starts[0] < 0.05 and ends else 0.0
    last = starts[-1] if starts and (not ends or ends[-1] < starts[-1] or abs(ends[-1] - total) < 0.1) else total
    if starts and ends and len(ends) == len(starts) and ends[-1] < total - 0.05:
        last = total                    # speech runs to the end
    elif starts and (len(ends) < len(starts)):
        last = starts[-1]               # trailing silence to the end of file
    return first, last, total


def ass_time(t):
    h, m = divmod(max(0.0, t), 3600); m, s = divmod(m, 60)
    return f'{int(h)}:{int(m):02d}:{s:05.2f}'


def title_card(ff, text, w, h, secs, fps, style, out):
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,{style.get('font', 'Montserrat')},{style.get('size', 64)},&H00E8F1F5,&H00E8F1F5,&H00000000,&H00000000,-1,0,0,0,100,100,0.5,0,1,0,0,5,90,90,0,1
Style: S,{style.get('font', 'Montserrat')},{int(style.get('size', 64) * 0.5)},&H00A6B3BF,&H00A6B3BF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,90,90,-{int(style.get('size', 64) * 1.6)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{ass_time(secs)},T,,0,0,0,,{{\\fad(250,250)}}{text}
"""
    a = out.with_suffix('.ass'); a.write_text(ass)
    subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'color=c=0x1B1F22:s={w}x{h}:r={fps}:d={secs}',
                    '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo:d={secs}',
                    '-vf', f"subtitles='{a}':fontsdir='{FONT_DIR}',format=yuv420p", '-c:v', 'libx264', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', str(out)], check=True)


def main(spec_path, out):
    ff = ffmpeg()
    spec = json.loads(Path(spec_path).read_text())
    base = Path(spec_path).parent
    w, h = spec.get('size', [1080, 1920]); fps = spec.get('fps', 25)
    hp, tp, gap = spec.get('head_pad', 0.15), spec.get('tail_pad', 0.35), spec.get('gap_black', 0.4)
    tmp = Path(out).parent / '_ugc_tmp'; tmp.mkdir(parents=True, exist_ok=True)
    parts, t = [], 0.0
    log = []
    sections = []
    for si, sec in enumerate(spec['sections']):
        sec_start = t
        if sec.get('title'):
            card = tmp / f'title{si}.mp4'
            title_card(ff, sec['title'], w, h, sec.get('title_secs', 2.0), fps, spec.get('title_style', {}), card)
            parts.append(card); t += sec.get('title_secs', 2.0)
        for ci, c in enumerate(sec['clips']):
            src = base / c if not Path(c).is_absolute() else Path(c)
            first, last, total = speech_bounds(ff, src)
            a = max(0.0, first - hp); b = min(total, last + tp)
            staged = tmp / f's{si}c{ci}.mp4'
            vf = (f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},format=yuv420p,'
                  f'trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS')
            af = f'aresample=48000,aformat=channel_layouts=stereo,atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={b - a - 0.06:.3f}:d=0.06'
            subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(src), '-vf', vf, '-af', af, '-c:v', 'libx264', '-crf', '18',
                            '-preset', 'fast', '-c:a', 'aac', '-b:a', '160k', str(staged)], check=True)
            log.append(f'{src.name}: speech {first:.2f} to {last:.2f} of {total:.2f}, kept {a:.2f} to {b:.2f} ({b - a:.1f}s), starts at {t:.2f}s')
            parts.append(staged); t += b - a
        sections.append({'title': sec.get('title', ''), 'start': round(sec_start, 3), 'end': round(t, 3)})
        if gap and si < len(spec['sections']) - 1:
            blk = tmp / f'gap{si}.mp4'
            subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'color=c=black:s={w}x{h}:r={fps}:d={gap}',
                            '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo:d={gap}', '-c:v', 'libx264', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(blk)], check=True)
            parts.append(blk); t += gap
    lst = tmp / 'list.txt'
    lst.write_text(''.join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c:v', 'libx264', '-crf', '19',
                    '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)], check=True)
    print('\n'.join(log)); print(f'total about {t:.1f}s')
    Path(out).with_suffix('.sections.json').write_text(json.dumps({'sections': sections}, indent=1))   # for captions-9x16.py clamp_ends
    target = {'web': (-14.0, -1.5), 'broadcast': (-24.0, -2.5)}.get(spec.get('loudness', 'web'))
    if target:
        sys.path.insert(0, str(Path(__file__).parent))
        from importlib import import_module
        st = import_module('stitch-commercial') if False else None
        # reuse the two-pass loudnorm from the stitch script
        src = Path(__file__).parent / 'stitch-commercial.py'
        ns = {}
        code = src.read_text().split("if __name__ == '__main__':")[0]
        exec(compile(code, str(src), 'exec'), ns)
        ns['normalise_loudness'](ff, Path(out), *target)
    shutil.rmtree(tmp, ignore_errors=True)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

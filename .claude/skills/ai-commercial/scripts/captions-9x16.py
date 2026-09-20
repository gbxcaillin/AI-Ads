"""Burn phone-readable captions into a 9:16 cut for silent autoplay.

Usage:
    python3 scripts/captions-9x16.py <cut9x16.mp4> <captions.json> <out.mp4> [--ass-only]

captions.json:
{
  "lines": ["Most businesses don't need more advice. They need a clearer picture.", "..."],
  "stop_at": 30.9,                 # optional: no captions after this time (the end card carries the words)
  "words": "cut-words.json"        # optional: word timings [{"w","s","e"}]; otherwise the cut is transcribed here
}

Why it works this way: the script is the source of the words (so a transcription
slip never reaches the screen), and the transcript is only the source of the
timing. Each sentence of a line becomes one caption, shown from a beat before its
first word until the next caption starts, so nothing flickers between phrases.
Captions sit in the phone-safe band (text bottom at 70 percent of the height,
70 px side margins), in the site's Montserrat SemiBold, off-white on a charcoal
box, which reads over a dark office and over a white web page alike. Rendered
with libass through ffmpeg's subtitles filter; audio is copied.
"""
import json
import re
import shutil
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

FONT_DIR = Path(__file__).parent / 'fonts'
STYLE = dict(font='Montserrat', size=76, colour='&H00E8F1F5', box='&H38221F1B', margin_v=576, margin_lr=70, pad=18)
MAX_CHARS = 42   # two lines at this size; a longer caption is split at a comma, or at the word nearest its middle


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def norm(w):
    return re.sub(r'[^a-z0-9]', '', w.lower())


def transcribe(ff, video):
    import tempfile
    wav = Path(tempfile.mkdtemp()) / 'a.wav'
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', str(wav)], check=True)
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(str(wav), word_timestamps=True, language='en')
    return [{'w': w.word.strip(), 's': w.start, 'e': w.end} for s in segs for w in s.words]


def sentences(line):
    """One caption per sentence; a long sentence is split at its commas (or at the
    word nearest its middle) so no caption runs past two lines on a phone."""
    out = []
    for sent in re.split(r'(?<=[.!?])\s+', line.strip()):
        if not sent:
            continue
        chunks = [sent]
        while any(len(c) > MAX_CHARS for c in chunks):
            c = next(c for c in chunks if len(c) > MAX_CHARS)
            i = chunks.index(c)
            commas = [m.end() for m in re.finditer(r',\s', c) if MAX_CHARS * 0.4 <= m.end() <= len(c) - 8]
            if commas:
                cut = min(commas, key=lambda k: abs(k - len(c) / 2))
            else:
                spaces = [m.start() for m in re.finditer(r' ', c)]
                cut = min(spaces, key=lambda k: abs(k - len(c) / 2)) + 1
            chunks[i:i + 1] = [c[:cut].rstrip(), c[cut:].lstrip()]
        out += chunks
    return out


def align(captions, words):
    """Map each caption's words onto the transcript with a sequence match, and return (start, end) per caption."""
    tw = [norm(w['w']) for w in words]
    tw_idx = [i for i, t in enumerate(tw) if t]           # transcript tokens that are real words
    tt = [tw[i] for i in tw_idx]
    cw, owner = [], []
    for ci, c in enumerate(captions):
        for w in c.split():
            n = norm(w)
            if n:
                cw.append(n); owner.append(ci)
    sm = SequenceMatcher(None, cw, tt, autojunk=False)
    hit = {}                                              # caption index -> list of transcript indices
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        if tag in ('equal', 'replace'):
            for k in range(min(a1 - a0, b1 - b0)):
                hit.setdefault(owner[a0 + k], []).append(tw_idx[b0 + k])
    spans = []
    for ci in range(len(captions)):
        idx = hit.get(ci)
        if not idx:
            sys.exit(f'could not place caption {ci + 1}: {captions[ci]!r}')
        spans.append((words[min(idx)]['s'], words[max(idx)]['e']))
    return spans


def ass_time(t):
    t = max(0.0, t)
    h, m = divmod(t, 3600); m, s = divmod(m, 60)
    return f'{int(h)}:{int(m):02d}:{s:05.2f}'


def build_ass(captions, spans, stop_at):
    s = STYLE
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{s['font']},{s['size']},{s['colour']},{s['colour']},{s['box']},{s['box']},-1,0,0,0,100,100,0.5,0,3,{s['pad']},0,2,{s['margin_lr']},{s['margin_lr']},{s['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for i, (text, (a, b)) in enumerate(zip(captions, spans)):
        start = a - 0.15
        nxt = spans[i + 1][0] - 0.15 if i + 1 < len(spans) else None
        end = b + 0.6
        if nxt is not None and nxt - end < 1.2:
            end = nxt                                     # hold to the next caption: no flicker between phrases
        if stop_at is not None:
            if start >= stop_at:
                continue
            end = min(end, stop_at)
        events.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{text}')
    return header + '\n'.join(events) + '\n'


def main(video, spec_path, out, ass_only=False):
    ff = ffmpeg()
    spec = json.loads(Path(spec_path).read_text())
    base = Path(spec_path).parent
    words = json.loads((base / spec['words']).read_text()) if spec.get('words') else transcribe(ff, video)
    captions = [c for line in spec['lines'] for c in sentences(line)]
    spans = align(captions, words)
    for c, (a, b) in zip(captions, spans):
        print(f'{a:6.2f} to {b:6.2f}  {c}')
    ass = build_ass(captions, spans, spec.get('stop_at'))
    ass_path = Path(out).with_suffix('.ass')
    ass_path.write_text(ass)
    if ass_only:
        print('wrote', ass_path); return
    vf = f"subtitles='{ass_path}':fontsdir='{FONT_DIR}'"
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(video), '-vf', vf, '-c:v', 'libx264', '-crf', '19',
                    '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(out)], check=True)
    print('wrote', out)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 3:
        sys.exit(__doc__)
    main(*args, ass_only='--ass-only' in sys.argv)

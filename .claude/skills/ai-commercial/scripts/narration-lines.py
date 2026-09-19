"""Write narration-lines.txt (start<TAB>end per line) for scripts/stitch-commercial.py.

Usage:
    python3 scripts/narration-lines.py <narration.mp4> <lines-out.txt> "first words of line 2" "first words of line 3" ...

The narration is transcribed with faster-whisper (word timestamps) to find where
each line begins, then every boundary is moved to the middle of the nearest pause
found by ffmpeg silencedetect, so no line is clipped: word timestamps tend to end
early, pauses do not. Line 1 starts at 0; the last line runs to the end of the file.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main(src, out, line_starts):
    ff = ffmpeg()
    err = subprocess.run([ff, '-i', src], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    total = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    err = subprocess.run([ff, '-hide_banner', '-i', src, '-af', 'highpass=f=120,silencedetect=n=-38dB:d=0.2',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    silences = list(zip([float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)],
                        [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]))
    wav = Path(tempfile.mkdtemp()) / 'n.wav'
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '16000', str(wav)], check=True)
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(str(wav), word_timestamps=True, language='en')
    words = [(w.start, w.end, re.sub(r'[^a-z0-9]', '', w.word.lower())) for s in segs for w in s.words]
    text = [w for _, _, w in words]
    print(' '.join(text))
    cuts = []
    pos = 0
    for phrase in line_starts:
        toks = [re.sub(r'[^a-z0-9]', '', t.lower()) for t in phrase.split()]
        hit = next(i for i in range(pos, len(words) - len(toks) + 1) if text[i:i + len(toks)] == toks)
        prev_end, start = words[hit - 1][1], words[hit][0]
        near = [s for s in silences if s[1] > prev_end - 0.4 and s[0] < start + 0.4]
        cut = (near[0][0] + near[0][1]) / 2 if near else (prev_end + start) / 2
        cuts.append(cut)
        pos = hit
    bounds = [0.0] + cuts + [total]
    lines = list(zip(bounds[:-1], bounds[1:]))
    Path(out).write_text(''.join(f'{a:.2f}\t{b:.2f}\n' for a, b in lines))
    for i, (a, b) in enumerate(lines):
        print(f'line {i + 1}: {a:.2f} to {b:.2f}')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

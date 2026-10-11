"""Check how a take says the abbreviation in "Your whole S M, S F, in one place."

The client wants four letters in two pairs: "S M", a quarter-beat pause, "S F".
Transcribers cannot be trusted to spell letters read aloud, so this counts the
syllable bursts in the waveform between the end of "whole" and the start of
"in", and reports the gaps between them. A pass is four bursts with the gap
after the second clearly the longest.

    python3 spots/libertystone-one/check_smsf.py <audio-or-video> [...]
"""
import subprocess, shutil, sys
import numpy as np
import imageio_ffmpeg
from faster_whisper import WhisperModel

FF = shutil.which('ffmpeg') or imageio_ffmpeg.get_ffmpeg_exe()
SR, HOP = 16000, 0.01
model = WhisperModel('small', device='cpu', compute_type='int8')

for path in sys.argv[1:]:
    raw = subprocess.run([FF, '-loglevel', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    segs, _ = model.transcribe(path, word_timestamps=True, language='en')
    words = [w for s in segs for w in s.words]
    text = ' '.join(w.word.strip() for w in words)
    whole = next((w for w in words if 'whole' in w.word.lower()), None)
    inw = next((w for w in words if w.word.strip().lower().startswith('in') and whole and w.start > whole.start), None)
    if not (whole and inw):
        print(f'{path}: could not find "whole ... in" in: {text}')
        continue
    t0, t1 = whole.end - 0.05, inw.start + 0.05
    n = int(HOP * SR)
    env = np.array([np.sqrt(np.mean(a[i:i + n] ** 2)) for i in range(int(t0 * SR), int(t1 * SR), n)])
    db = 20 * np.log10(env + 1e-9)
    db = np.convolve(db, np.ones(3) / 3, 'same')
    thr = db.max() - 14                                   # a burst is within 14 dB of the loudest
    on = db > thr
    bursts, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            if (j - i) * HOP >= 0.04:                      # ignore clicks shorter than 40 ms
                bursts.append((t0 + i * HOP, t0 + j * HOP))
            i = j
        else:
            i += 1
    # drop fragments of "whole" and "in" that touch the window edges
    bursts = [b for b in bursts if b[0] > t0 + HOP * 1.5 and b[1] < t1 - HOP * 1.5]
    gaps = [bursts[k + 1][0] - bursts[k][1] for k in range(len(bursts) - 1)]
    ok = len(bursts) == 4 and len(gaps) == 3 and gaps[1] > max(gaps[0], gaps[2]) + 0.04
    print(f'{path}\n  transcript: {text}\n  abbreviation {t0:.2f}-{t1:.2f}s: {len(bursts)} bursts '
          + ' '.join(f'[{b0:.2f}-{b1:.2f}]' for b0, b1 in bursts)
          + '\n  gaps: ' + ', '.join(f'{g * 1000:.0f} ms' for g in gaps)
          + f'\n  {"PASS: S M | S F" if ok else "CHECK: not the S M | S F shape"}')

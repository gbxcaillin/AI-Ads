"""Find where each exported clip starts on the switched-edit clock by matching its sound to a mic window padded 3 s each side (src/<n>-micpad.wav), cut the mic to the clip span, and write src/windows.json. Run from spots/pearl-interview/src."""
import json, subprocess, numpy as np, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 8000
def pcm(p):
    raw = subprocess.run([FF, '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return (x - x.mean()) / (x.std() + 1e-9)
nominal = {'A': (529.9, 15.5), 'B': (947.6, 17.0), 'C': (1100.4, 11.5)}
win = {}
for n, (s, d) in nominal.items():
    clip, mic = pcm(f'{n}-sw.mp4'), pcm(f'{n}-micpad.wav')
    N = 1 << int(np.ceil(np.log2(len(mic) + len(clip))))
    c = np.fft.irfft(np.fft.rfft(mic, N) * np.conj(np.fft.rfft(clip, N)), N)[:len(mic) - len(clip) + 1]
    k = int(np.argmax(c)); peak = c[k] / len(clip)
    start = (s - 3.0) + k / SR                         # clip start on the switched clock
    dur = float(subprocess.run([FF, '-i', f'{n}-sw.mp4'], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')[-1])
    print(f'{n}: clip starts at switched {start:.3f} s (nominal {s}), corr {peak:.2f}, dur {dur:.2f}')
    # mic window cut to exactly the clip's span
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{k / SR:.4f}', '-t', f'{dur:.3f}', '-i', f'{n}-micpad.wav', '-c:a', 'pcm_s24le', f'{n}-mic.wav'], check=True)
    win[n] = {'start': round(start, 3), 'dur': round(dur - 0.05, 3)}
json.dump(win, open('windows.json', 'w'), indent=1); print(win)

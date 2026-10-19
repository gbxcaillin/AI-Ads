"""Pearl founder interview: build the cut from cut.json.

Sources are short windows pulled from the Drive files (see fetch_sources.sh), named
src/<window>-sw.mp4 (switched edit, picture and desk sound) and optionally src/<window>-mic.wav
(the clean mic). Each window file records its start time on the switched clock in src/windows.json.

Every answer is built from its parts: picture from the switched edit, alternating a wide and a
punch-in framing at each internal cut so no jump cut shows; sound from the mic when present
(aligned by cross-correlation against the switched audio), else the switched audio; 12 ms ramps
on every audio edit. Question cards and the end card come from cards/ (design.mjs).
Output: out/pearl-interview-v<N>.mp4, 1920x1080, 25 fps, yuv420p, -14 LUFS / -1 dBTP.

Run from the repo root:  python3 spots/pearl-interview/build_cut.py [--version N] [--src DIR]
"""
import json, os, subprocess, sys, tempfile
import numpy as np
import imageio_ffmpeg

D = 'spots/pearl-interview'
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, SR = 1920, 1080, 25, 48000
PUNCH = 1.18                       # punch-in scale for the alternate framing
PUNCH_CY = 0.36                    # vertical centre of the punch-in (eyes stay at the same height)
args = sys.argv[1:]
VER = args[args.index('--version') + 1] if '--version' in args else '1'
SRC = args[args.index('--src') + 1] if '--src' in args else f'{D}/src'
cut = json.load(open(f'{D}/cut.json'))
windows = json.load(open(f'{SRC}/windows.json'))      # {"A": {"start": 529.9, "mic_offset": 50.66}, ...}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-3000:])
    return r.stderr

def window_for(t0, t1):
    for k, w in windows.items():
        if w['start'] <= t0 and t1 <= w['start'] + w['dur']: return k, w
    sys.exit(f'no source window covers {t0}-{t1}')

def pcm(path, ss, dur):
    raw = subprocess.run([FF, '-v', 'error', '-ss', f'{ss:.4f}', '-t', f'{dur:.4f}', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)

def mic_lag(k, w):
    """fine offset of the mic window against the switched audio, in seconds (mic = switched + lag)"""
    if 'mic_lag' in w: return w['mic_lag']
    a = pcm(f'{SRC}/{k}-sw.mp4', 0, w['dur'])[::6]; b = pcm(f'{SRC}/{k}-mic.wav', 0, w['dur'])[::6]   # 8 kHz
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    lag = int(np.argmax(np.r_[c[:4000], c[-4000:]])); lag = lag if lag < 4000 else lag - 8000
    w['mic_lag'] = lag / 8000.0
    print(f'window {k}: mic lags switched audio by {w["mic_lag"] * 1000:.1f} ms')
    return w['mic_lag']

tmp = tempfile.mkdtemp(prefix='pearl-')
pieces = []
venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
aenc = ['-c:a', 'pcm_s16le', '-ar', str(SR), '-ac', '2']

def still(png, dur, name):
    out = f'{tmp}/{name}.mov'
    run([FF, '-y', '-loop', '1', '-framerate', str(FPS), '-t', f'{dur}', '-i', png,
         '-f', 'lavfi', '-t', f'{dur}', '-i', f'anullsrc=r={SR}:cl=stereo',
         '-vf', f'scale={W}:{H},format=yuv420p', *venc, *aenc, '-shortest', out])
    return out

for si, seg in enumerate(cut['timeline']):
    if seg['kind'] == 'card':
        pieces.append(still(f'{D}/cards/{seg["card"]}.png', seg['dur'], f'{si:02d}-card'))
        continue
    if seg['kind'] == 'end':
        pieces.append(still(f'{D}/cards/end-card.png', seg['dur'], f'{si:02d}-end'))
        continue
    parts = []
    for pi, (t0, t1, framing) in enumerate(seg['parts']):
        k, w = window_for(t0, t1)
        ss, dur = t0 - w['start'], t1 - t0
        vf = f'scale={W}:{H}'
        if framing == 'punch-in':
            cw, ch = W / PUNCH, H / PUNCH
            vf = f'crop={cw:.0f}:{ch:.0f}:{(W - cw) / 2:.0f}:{(H - ch) * PUNCH_CY / 0.5 / 2:.0f},scale={W}:{H}:flags=lanczos'
        out = f'{tmp}/{si:02d}-{pi}.mov'
        if os.path.exists(f'{SRC}/{k}-mic.wav'):
            mss = ss + mic_lag(k, w)
            ain = ['-ss', f'{mss:.4f}', '-t', f'{dur:.4f}', '-i', f'{SRC}/{k}-mic.wav']
        else:
            ain = ['-ss', f'{ss:.4f}', '-t', f'{dur:.4f}', '-i', f'{SRC}/{k}-sw.mp4']
        fade = f'afade=t=in:d=0.012,afade=t=out:st={dur - 0.012:.4f}:d=0.012'
        run([FF, '-y', '-ss', f'{ss:.4f}', '-t', f'{dur:.4f}', '-i', f'{SRC}/{k}-sw.mp4', *ain,
             '-map', '0:v', '-map', '1:a', '-vf', f'{vf},fps={FPS},format=yuv420p',
             '-af', f'aresample={SR},pan=stereo|c0=c0|c1=c0,{fade}', *venc, *aenc, '-t', f'{dur:.4f}', out])
        parts.append(out)
    lst = f'{tmp}/{si:02d}.txt'
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    joined = f'{tmp}/{si:02d}-answer.mov'
    run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined])
    if seg.get('name_super'):
        sup = f'{tmp}/{si:02d}-answer-super.mov'
        run([FF, '-y', '-i', joined, '-loop', '1', '-framerate', str(FPS), '-i', f'{D}/cards/name-super.png',
             '-filter_complex', '[1:v]format=rgba,fade=t=in:st=0.4:d=0.3:alpha=1,fade=t=out:st=3.6:d=0.3:alpha=1[s];[0:v][s]overlay=shortest=1,format=yuv420p',
             '-map', '0:a', *venc, '-c:a', 'copy', sup])
        joined = sup
    if seg.get('cutaway'):
        # OpenArt cutaway over the answer: picture only, Andrew's voice continues under it.
        # It starts just before an internal edit so the join is never seen; 0.3 s dissolves.
        c = seg['cutaway']; st, du = c['at'], c['dur']
        cw = f'{tmp}/{si:02d}-answer-cut.mov'
        run([FF, '-y', '-i', joined, '-i', f'{D}/{c["file"]}', '-filter_complex',
             f'[1:v]trim=start={c.get("from", 0)}:duration={du},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,'
             f'unsharp=5:5:0.6,noise=alls=6:allf=t,fps={FPS},format=yuva420p,'
             f'fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st={du - 0.3:.3f}:d=0.3:alpha=1,setpts=PTS+{st}/TB[b];'
             f'[0:v][b]overlay=eof_action=pass,format=yuv420p',
             '-map', '0:a', *venc, '-c:a', 'copy', cw])
        joined = cw
    pieces.append(joined)

lst = f'{tmp}/all.txt'
open(lst, 'w').write(''.join(f"file '{p}'\n" for p in pieces))
raw = f'{tmp}/raw.mov'
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', raw])

# two-pass loudness to web delivery
m = run([FF, '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
os.makedirs(f'{D}/out', exist_ok=True)
out = f'{D}/out/pearl-interview-v{VER}.mp4'
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
      f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
run([FF, '-y', '-i', raw, '-af', f'{ln},aresample={SR}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
     '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out])
m2 = run([FF, '-i', out, '-af', 'loudnorm=I=-14:TP=-1.5:print_format=json', '-f', 'null', '-'])
j2 = json.loads(m2[m2.rindex('{'):m2.rindex('}') + 1])
print(f'wrote {out}: input {js["input_i"]} LUFS -> {j2["input_i"]} LUFS, true peak {j2["input_tp"]} dBTP')

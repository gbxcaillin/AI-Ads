"""Synthesise the LibertyStone sound-design layer as one stereo WAV the length
of the cut: soft notification pings through the overload (getting closer
together), key clicks accelerating through the friction, nothing on the
exhale, one soft chime as the logo lands. Kept low; it sits with the bed,
under the voice. Times are cut seconds.
    python3 spots/libertystone-one/make_sfx.py <total_seconds> <out.wav> [chime_seconds]
"""
import sys, wave
import numpy as np

SR = 48000
total = float(sys.argv[1])
out = sys.argv[2]
CHIME_AT = float(sys.argv[3]) if len(sys.argv) > 3 else 25.9
mix = np.zeros(int(total * SR) + SR, np.float32)
rng = np.random.default_rng(11)


def place(sig, t, gain):
    i = int(t * SR)
    mix[i:i + len(sig)] += sig[:len(mix) - i] * gain


def ping(f1, f2, dur=0.55):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 9) * np.minimum(1, t / 0.004)
    return (np.sin(2 * np.pi * f1 * t) * 0.6 + np.sin(2 * np.pi * f2 * t) * 0.4) * env


def click():
    n = int(0.018 * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    body = np.sin(2 * np.pi * 2400 * t) * 0.5 + noise * 0.5
    return body * np.exp(-t * 320)


def chime(dur=3.2):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 1.6) * np.minimum(1, t / 0.01)
    tone = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((660, 0.55), (990, 0.3), (1320, 0.18), (1980, 0.07)))
    return tone * env


# overload 4.0 to 13.0: pings arrive more often as the desk fills
for k, t in enumerate([5.4, 7.6, 9.2, 10.3, 11.1, 11.7, 12.2, 12.6]):
    f = [1318, 1175, 1568, 1318, 1760, 1175, 1568, 1397][k]
    place(ping(f, f * 1.5), t, 0.10 + 0.012 * k)
# friction 13.0 to 16.4: key clicks, accelerating, cut dead at the exhale
t, gap = 13.05, 0.32
while t < 16.3:
    place(click(), t + rng.uniform(-0.01, 0.01), 0.16)
    t += gap
    gap = max(0.075, gap * 0.9)
# logo: one soft chime as the mark settles
place(chime(), CHIME_AT, 0.20)

mix = mix[:int(total * SR)]
st = np.stack([mix, mix], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out, round(total, 2), 's')

"""brightday "seven steps": the logo animation built in code from the real assets.

The seven petals of the mark break apart into a ring, fly into a staircase of
seven flat steps with long diagonal shadows, the b jumps in from off screen
left onto step 1 and hops up all seven, then leaps; the steps swirl around it
in a tightening spiral and lock back into the mark, the b lands beside it and
the rest of the word stretches out from behind the b, pushing the mark into
its corner. The last second crossfades to frames/end-frame.png, the supplied
logo, so the final frame is the logo exactly.

Needs brand/petals.npz (extract_petals.py) and frames/end-frame.png.
Run from the repo root:
  python3 spots/brightday-logo-steps/render_steps.py            # full video
  python3 spots/brightday-logo-steps/render_steps.py --strip    # key-frame strip only
Writes out/brightday-steps-code-v1.mp4 (1920x1080, 24 fps, yuv420p, silent).
"""
import sys, subprocess, numpy as np, cv2
import imageio_ffmpeg

D = 'spots/brightday-logo-steps'
W, H, FPS, DUR = 1920, 1080, 24, 9.5
SUB = 3                      # motion-blur subframes per frame (180 degree shutter)
NAVY = np.array([0x5A, 0x35, 0x13], np.float32)          # BGR, the logo's own navy
PINK = np.array([0x70, 0x08, 0xF0], np.float32)
GARNET = np.array([0x48, 0x08, 0x98], np.float32)
SIDE = np.array([0x30, 0x03, 0x5E], np.float32)          # step edge, garnet in shadow

# ---------- assets ----------
z = np.load(f'{D}/brand/petals.npz')
masks = np.unpackbits(z['bits'], axis=-1)[..., :int(z['shape'][2])].astype(bool)
MC = z['centre'].astype(np.float64)                      # mark centre, webp pixels
STEP = float(z['step'])
MS = 0.3                                                 # master sprite scale
PET = np.array([cv2.resize(m.astype(np.float32), None, fx=MS, fy=MS, interpolation=cv2.INTER_AREA) for m in masks])
CK = np.array([np.argwhere(m)[:, ::-1].mean(0) for m in masks])   # petal centroids, webp px
VK = CK - MC                                                       # offsets from mark centre
THK = np.degrees(np.arctan2(VK[:, 1], VK[:, 0]))

def R(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])    # y down: positive turns clockwise on screen

# flat orientation of each petal: the turn that gives the lowest silhouette (long edge level)
def flat_angle(k):
    pts = np.argwhere(masks[k][::4, ::4])[:, ::-1] * 4.0 - CK[k]
    hs = [(np.ptp(pts @ R(a).T[:, 1]), a) for a in np.arange(-90, 90, 0.5)]
    return min(hs)[1]
AFLAT = np.array([flat_angle(k) for k in range(7)])

bspr = cv2.imread(f'{D}/brand/b-white.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
word = cv2.imread(f'{D}/brand/wordmark-white.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
word[:, :153] = 0            # drop the b (ink ends at 147, r starts at 160)
word[:, 1160:] = 0           # drop the sliver of the mark at the right of the crop
for s in (bspr, word):
    s[..., :3] *= s[..., 3:] / 255.0                     # premultiply

# ---------- final layout (logo 2000x1000 scaled 0.96, padded 60 px top) ----------
LS, LY = 0.96, 60.0
SM = 243 / 2000 * LS                                     # mark scale, webp px -> frame px
M_FINAL = np.array([1556 * LS, 234 * LS + LY]) + SM * MC  # mark centre in the final frame
M_LEFT_F = 1556 * LS
B_ANCHOR = np.array([75.5, 236.0])                       # b sprite: ink bottom centre
B_FINAL = np.array([394 * LS, 360 * LS + LY]) + B_ANCHOR * LS
B_HALF = (145 - 6) / 2 * LS                              # half ink width of the b
B_HC = (236 - 12) / 2 * LS                               # half ink height
WORD_X0, WORD_Y0 = 392 * LS, 360 * LS + LY
WORD_RIGHT_F = WORD_X0 + 1159 * LS
GAP_F = M_LEFT_F - WORD_RIGHT_F
# b and mark side by side before the word: the pair is centred
PAIR_GAP = 34.0
MARK_W = 2000 * SM
B0 = np.array([W / 2 - (2 * B_HALF + PAIR_GAP + MARK_W) / 2 + B_HALF, B_FINAL[1]])
M_LEFT0 = B0[0] + B_HALF + PAIR_GAP
M0 = np.array([M_LEFT0 + SM * MC[0], M_FINAL[1]])

# ---------- easing ----------
def cl(x): return float(np.clip(x, 0, 1))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def eio(x): x = cl(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eout(x): x = cl(x); return 1 - (1 - x) ** 3
def ph(t, a, b): return cl((t - a) / (b - a))
def lerp(a, b, u): return a + (b - a) * u

# ---------- timeline ----------
T_BREAK, T_RING = 0.8, 1.6
T_ENTER, T_LAND0, HOP = 2.6, 3.05, 0.35
LANDS = [T_LAND0 + j * HOP for j in range(7)]            # b lands on step j at LANDS[j]
T_LEAP = LANDS[6]                                        # 5.15
T_SW0, T_SW1 = 5.3, 6.7                                  # swirl
T_REV0, T_REV1 = 7.0, 7.9                                # word stretches out
T_LOCK0, T_LOCK1 = 8.0, 8.4                              # crossfade to the supplied logo

S0, C0 = 0.18, np.array([W / 2, H / 2])                  # opening mark, 360 px wide
S_STEP, RING_R, S_RING = 0.26, 330.0, 0.2
STEP_X = np.array([300 + i * 215 for i in range(7)], float)
STEP_Y = np.array([940 - i * 95 for i in range(7)], float)
HOVER = np.array([1180.0, 340.0])                        # b bottom centre at the top of the leap
DRIFT = np.array([760.0, 310.0])

def spin_open(t):            # slow turn of the whole mark through the opening and the break
    return 6 * ph(t, 0, T_BREAK) + 34 * eio(ph(t, T_BREAK, T_RING))

def ring_state(k, t):
    u = eio(ph(t, T_BREAK, T_RING))
    sp = spin_open(t)
    r = lerp(1.0, RING_R / (S0 * 653), u)
    breath = 1 - 0.035 * np.sin(np.pi * ph(t, 0.55, T_BREAK + 0.2))   # little inhale before it unlocks
    P = C0 + R(sp) @ VK[k] * S0 * r * breath
    return P, lerp(S0, S_RING, u), sp, 0.0

# steps: assign petals to steps by their x on the ring, leftmost goes to step 1
ring_x = [ring_state(k, T_RING)[0][0] for k in range(7)]
STEP_OF = {k: i for i, k in enumerate(np.argsort(ring_x))}
def nearest_mod(a, ref, period=180):
    return a + period * np.round((ref - a) / period)
A_STEP = np.array([nearest_mod(AFLAT[k], spin_open(T_RING)) for k in range(7)])

def step_top(i, t):
    y = STEP_Y[i] + 5 * np.sin(2 * np.pi * (0.45 * t + i / 7))
    tau = t - LANDS[i]
    if tau > 0: y += 16 * np.sin(18 * tau) * np.exp(-7 * tau)     # gives under the b
    return np.array([STEP_X[i], y])

def step_state(k, t):
    i = STEP_OF[k]
    u = eio(ph(t, T_RING + 0.07 * i, T_RING + 0.07 * i + 0.62))
    P0, s0, a0, _ = ring_state(k, T_RING)
    P1 = step_top(i, t)
    P = lerp(P0, P1, u) + np.array([0, -150 * np.sin(np.pi * u)])
    return P, lerp(s0, S_STEP, u), lerp(a0, A_STEP[k], u), u

def swirl_state(k, t):
    u = ph(t, T_SW0, T_SW1)
    e1, e2 = eio(u), ss(u)
    hover_c = b_state(T_SW0)[0] + np.array([0, -B_HC])
    SC = lerp(hover_c, M0, e2)
    spin = 600 * (1 - e1)
    q = lerp(0.45, 1.0, e1)
    rad = lerp(390 / (SM * 653), 1.0, e1)
    v = R(spin) @ VK[k] * SM * rad
    depth = np.sin(np.radians(THK[k] + spin))
    v[1] *= q
    s = lerp(0.2, SM, e1) * (1 + 0.14 * (1 - e1) * depth)
    return SC + v, s, lerp(A_STEP[k], 0, e1) + spin, lerp(0.75, 0, e1)

def mark_left(t):
    p = eio(ph(t, T_REV0, T_REV1))
    bx = lerp(B0[0], B_FINAL[0], p)
    wr = bx + (WORD_RIGHT_F - B_FINAL[0]) * p
    return max(M_LEFT0, wr + GAP_F), bx, p

def petal_state(k, t):
    if t < T_RING:
        return ring_state(k, t)
    if t < T_LEAP:
        return step_state(k, t)
    if t < T_SW1:
        P1, s1, a1, f1 = step_state(k, t)
        P2, s2, a2, f2 = swirl_state(k, t)
        d = 0.05 * (6 - STEP_OF[k])                       # top step lifts first
        w = ss(ph(t, T_LEAP + d, T_LEAP + d + 0.65))
        return lerp(P1, P2, w), lerp(s1, s2, w), lerp(a1, a2, w), lerp(f1, f2, w)
    ml = mark_left(t)[0]
    pulse = 1 + 0.045 * np.sin(np.pi * ph(t, T_SW1, T_SW1 + 0.3))   # the lock
    Mc = np.array([ml + SM * MC[0], M0[1]])
    return Mc + VK[k] * SM * pulse, SM * pulse, 0.0, 0.0

# ---------- the b ----------
def hop(p0, p1, tau, h):
    x = lerp(p0[0], p1[0], tau)
    y = lerp(p0[1], p1[1], tau) - 4 * h * tau * (1 - tau)
    return np.array([x, y])

def b_state(t):
    """bottom centre, (sx, sy), rotation, visible"""
    squash = sum(0.16 * np.exp(-((t - tl - 0.035) / 0.045) ** 2) for tl in LANDS)
    squash += 0.15 * np.exp(-((t - (T_SW1 + 0.17) - 0.035) / 0.05) ** 2)     # landing beside the mark
    rot = 0.0
    if t < T_ENTER:
        pos, stretch = np.array([-200.0, 1000.0]), 0.0
    elif t < T_LAND0:
        tau = ph(t, T_ENTER, T_LAND0)
        pos = hop(np.array([-140.0, 1010.0]), step_top(0, t), tau, 260)
        stretch = 0.08 * np.sin(np.pi * tau); rot = 10 * (1 - tau) - 4 * np.sin(np.pi * tau)
    elif t < T_LEAP:
        j = min(int((t - T_LAND0) / HOP), 5)
        tau = (t - LANDS[j]) / HOP
        tf = cl((tau - 0.18) / 0.82)
        pos = hop(step_top(j, t), step_top(j + 1, t), tf, 120) if tau > 0.18 else step_top(j, t)
        stretch = 0.07 * np.sin(np.pi * tf)
    elif t < T_SW1 + 0.17:
        tc = T_LEAP + 0.1
        if t < tc:
            pos, stretch = step_top(6, t), 0.0
        elif t < 5.75:
            tau = ph(t, tc, 5.75)
            pos = np.array([lerp(STEP_X[6], HOVER[0], eout(tau)),
                            lerp(step_top(6, tc)[1], HOVER[1], eout(tau)) - 70 * np.sin(np.pi * tau)])
            stretch = 0.08 * np.sin(np.pi * tau)
        elif t < 6.45:
            tau = eio(ph(t, 5.75, 6.45))
            pos, stretch = lerp(HOVER, DRIFT, tau), 0.0
        else:
            tau = ph(t, 6.45, T_SW1 + 0.17)
            pos = np.array([lerp(DRIFT[0], B0[0], eout(tau)), lerp(DRIFT[1], B0[1], tau * tau) - 50 * np.sin(np.pi * tau)])
            stretch = 0.06 * np.sin(np.pi * tau)
        rot = -360 * eio(ph(t, 5.55, 6.4))
    else:
        bx = mark_left(t)[1]
        pos, stretch = np.array([bx, B0[1]]), 0.0
    sy = 1 - squash + stretch
    return pos, (1 / np.sqrt(sy), sy), rot, t >= T_ENTER - 0.05

def b_matrix(t):
    pos, (sx, sy), rot, vis = b_state(t)
    # sprite -> frame: anchor at ink bottom centre, squash about the feet, turn about the middle
    A = np.diag([sx * LS, sy * LS])
    c = np.array([0, -B_HC * sy])
    Rm = R(rot)
    M = Rm @ A
    off = pos + c - Rm @ c - M @ B_ANCHOR
    return np.c_[M, off], vis

# ---------- drawing ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
KEY = np.exp(-(((xx - W / 2) / (W * .42)) ** 2 + ((yy - H * .36) / (H * .55)) ** 2))
VIG = .42 + .58 * np.clip(1 - (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .70)) ** 2) ** 1.2 * .75, 0, 1)
LIGHT_ADD = KEY[..., None] * np.array([22, 14, 6], np.float32)
def light(img):
    return np.clip(img * VIG[..., None] + LIGHT_ADD, 0, 255)

SH_DIR = np.array([1.0, 0.62]); SH_DIR /= np.linalg.norm(SH_DIR)
def long_shadow(occ, length):
    q = cv2.resize(occ, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    acc = np.zeros_like(q); n = 36
    for j in range(1, n + 1):
        d = SH_DIR * length / 4 * j / n
        sh = cv2.warpAffine(q, np.float32([[1, 0, d[0]], [0, 1, d[1]]]), (W // 4, H // 4))
        acc = np.maximum(acc, sh * (1 - j / (n + 1)) ** 1.3)
    acc = cv2.GaussianBlur(acc, (0, 0), 3)
    return cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)

def shadow_weight(t):
    return ss(ph(t, 0.9, 1.9)) * (1 - ss(ph(t, 5.6, 6.8)))

def warp_petal(k, P, s, a, f):
    sq = 1 - 0.45 * f
    A = np.diag([1, sq]) @ R(a) * (s / MS)
    off = P - A @ (CK[k] * MS)
    return cv2.warpAffine(PET[k], np.c_[A, off].astype(np.float32), (W, H), flags=cv2.INTER_LINEAR)

def render(t):
    img = np.empty((H, W, 3), np.float32); img[:] = NAVY
    tops, sides = [], np.zeros((H, W), np.float32)
    for k in range(7):
        P, s, a, f = petal_state(k, t)
        m = warp_petal(k, P, s, a, f)
        tops.append(m)
        th = int(round(28 * f * s / S_STEP))
        if th > 0:
            ext = cv2.dilate(m, np.ones((th + 1, 1), np.uint8), anchor=(0, th))
            sides = np.maximum(sides, ext)
    cov = np.sum(tops, 0)
    top_a = np.clip(cov, 0, 1)
    g = np.clip(cov - 1, 0, 1)[..., None]
    top_c = PINK * (1 - g) + GARNET * g

    # word (rest of it, after the b), stretched out from behind the b
    ml, bx, p = mark_left(t)
    word_l = None
    if p > 0:
        sx = p
        A = np.float32([[sx * LS, 0, bx + sx * (WORD_X0 - B_FINAL[0])], [0, LS, WORD_Y0]])
        word_l = cv2.warpAffine(word, A, (W, H), flags=cv2.INTER_LINEAR)
        word_l[:, :int(bx + B_HALF + 2)] = 0                    # hidden behind the b

    Mb, bvis = b_matrix(t)
    b_l = cv2.warpAffine(bspr, Mb.astype(np.float32), (W, H), flags=cv2.INTER_LINEAR) if bvis else None

    w = shadow_weight(t)
    if w > 0:
        occ = np.maximum(top_a, sides)
        if b_l is not None: occ = np.maximum(occ, b_l[..., 3] / 255)
        sh = long_shadow(occ, 300) * w
        img *= (1 - 0.7 * sh)[..., None]
    if sides.max() > 0:
        sa = np.clip(sides - top_a, 0, 1)[..., None]
        img = img * (1 - sa) + SIDE * sa
    ta = top_a[..., None]
    img = img * (1 - ta) + top_c * ta
    for L in (word_l, b_l):
        if L is not None:
            a = L[..., 3:] / 255
            img = img * (1 - a) + L[..., :3]
    return img

END = cv2.imread(f'{D}/frames/end-frame.png').astype(np.float32)
BG_LIT = light(np.broadcast_to(NAVY, (H, W, 3)).copy())
EL = np.clip((END.mean(-1) - BG_LIT.mean(-1)) / 50, 0, 1)[..., None]

def frame(n):
    t = n / FPS
    if t >= T_LOCK1:
        out = END.copy()
    else:
        acc = np.zeros((H, W, 3), np.float32)
        for j in range(SUB):
            acc += render(t + (j - (SUB - 1) / 2) / (SUB * 2 * FPS) * (1 if SUB > 1 else 0))
        out = light(acc / SUB)
        if t > T_LOCK0:
            w = ss(ph(t, T_LOCK0, T_LOCK1))
            out = out * (1 - w) + END * w
    # slow light sweep across the finished logo
    u = ph(t, 8.45, 9.3)
    if 0 < u < 1:
        pos = lerp(-500, W + 900, eio(u))
        band = np.exp(-(((xx + 0.45 * yy) - pos) / 110) ** 2)[..., None]
        out = out + band * EL * 70
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    import os
    os.makedirs(f'{D}/out', exist_ok=True)
    N = int(round(DUR * FPS))
    if '--strip' in sys.argv:
        ts = [0.4, 1.2, 1.9, 2.4, 2.85, 3.3, 4.2, 5.0, 5.5, 5.9, 6.3, 6.75, 7.2, 7.5, 7.8, 9.0]
        tiles = [cv2.resize(frame(int(round(t * FPS))), (480, 270), interpolation=cv2.INTER_AREA) for t in ts]
        for t, im in zip(ts, tiles):
            cv2.putText(im, f'{t:.2f}s', (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
        cv2.imwrite(f'{D}/out/strip-code-v1.png', np.vstack(rows))
        print('wrote out/strip-code-v1.png')
        sys.exit()
    for a in sys.argv[1:]:
        if a.startswith('--frame='):
            t = float(a.split('=')[1]); cv2.imwrite(f'{D}/out/frame-{t:.2f}.png', frame(int(round(t * FPS)))); sys.exit()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = f'{D}/out/brightday-steps-code-v1.mp4'
    p = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(N):
        p.stdin.write(frame(n).tobytes())
        if n % 24 == 0: print(f'{n / FPS:.1f}s', flush=True)
    p.stdin.close(); p.wait()
    print('wrote', out)

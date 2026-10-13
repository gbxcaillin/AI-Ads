"""Split the Brightday mark into its 7 petals and save them as masks.

The mark is one pink shape (#F00870) with garnet (#980848) where two petals
overlap. A watershed on the pink region seeded at the 7 petal centres gives
each petal its own pink; each petal then takes the garnet overlaps it touches.
As a cross-check every petal is also rebuilt as one clean petal rotated by
k * 360/7 about the fitted mark centre; the set that rebuilds the mark more
exactly is kept.
Check: coverage 1 must equal the pink and coverage 2 the garnet.

Run from the repo root:  python3 spots/brightday-logo-steps/extract_petals.py
Writes brand/petals.npz (bit-packed masks, the centre and the step angle).
"""
import numpy as np, cv2

D = 'spots/brightday-logo-steps'
m = cv2.imread(f'{D}/brand/brightday-mark.webp', cv2.IMREAD_UNCHANGED)
H, W = m.shape[:2]
alpha = m[..., 3] > 127
bgr = m[..., :3].astype(int)
dp = np.abs(bgr - [0x70, 0x08, 0xF0]).sum(-1)
dg = np.abs(bgr - [0x48, 0x08, 0x98]).sum(-1)
pink, garnet = alpha & (dp < dg), alpha & (dg <= dp)

# seeds: the petals sit on a ring; centroids found by the first pass were at
# about 653 px from the centre, the first at -147.1 degrees, then +360/7 each
ys, xs = np.nonzero(alpha)
c0 = np.array([xs.mean(), ys.mean()])
step = 360 / 7
seeds = [c0 + 653 * np.array([np.cos(np.radians(-147.1 + k * step)), np.sin(np.radians(-147.1 + k * step))]) for k in range(7)]

dist = cv2.distanceTransform(pink.astype(np.uint8), cv2.DIST_L2, 5)
markers = np.zeros((H, W), np.int32)
markers[~alpha] = 8
for k, (sx, sy) in enumerate(seeds):
    cv2.circle(markers, (int(sx), int(sy)), 20, k + 1, -1)
markers[~pink & alpha] = 0
img = cv2.cvtColor(cv2.normalize(-dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_GRAY2BGR)
lab = cv2.watershed(img, markers.copy())

ncomp, gl = cv2.connectedComponents(garnet.astype(np.uint8))
ker = np.ones((5, 5), np.uint8)
P = []
for k in range(7):
    own = (lab == k + 1) & pink
    near = cv2.dilate(own.astype(np.uint8), ker) > 0
    touch = set(np.unique(gl[near & garnet])) - {0}
    P.append(own | np.isin(gl, list(touch)))
P = np.array(P)

# centre: circle through the petal centroids
C = np.array([np.argwhere(p)[:, ::-1].mean(0) for p in P])
A = np.c_[2 * C, np.ones(7)]
cx, cy, c = np.linalg.lstsq(A, (C ** 2).sum(1), rcond=None)[0]

def rot(mask, ang):
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1)  # positive = anticlockwise on screen
    return cv2.warpAffine(mask.astype(np.float32), M, (W, H)) > 0.5

def iou(a, b): return (a & b).sum() / (a | b).sum()

# pick the template whose rotations agree best with the watershed petals
best = max(range(7), key=lambda t: sum(iou(rot(P[t], -(k - t) * step), P[k]) for k in range(7)))
Q = np.array([P[best] if k == best else rot(P[best], -(k - best) * step) for k in range(7)])
def mismatch(S):
    cov = S.sum(0)
    return (pink != (cov == 1)).sum() + (garnet != (cov >= 2)).sum()
print('template petal', best, 'IoU per petal', [round(iou(Q[k], P[k]), 4) for k in range(7)])
print('mismatch watershed', mismatch(P), 'rotated', mismatch(Q))
# keep whichever set rebuilds the mark more exactly
if mismatch(P) < mismatch(Q): Q = P
mis = mismatch(Q)
print(f'coverage mismatch {mis} px = {100 * mis / alpha.sum():.3f} % of the mark')
assert mis / alpha.sum() < 0.005
np.savez_compressed(f'{D}/brand/petals.npz', bits=np.packbits(Q, axis=-1), shape=np.array(Q.shape),
                    centre=np.array([cx, cy]), step=step)
print('wrote brand/petals.npz, centre', round(cx, 2), round(cy, 2))

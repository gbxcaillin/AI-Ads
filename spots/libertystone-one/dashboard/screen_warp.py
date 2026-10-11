"""Warp the LibertyStone dashboard onto the laptop screen.

Used two ways:
  1. check the fit on the plate still:   python3 screen_warp.py check
  2. per-frame on the animated plate:    imported by track_and_composite.py

SCREEN is the inner edge of the bezel in plate-A pixel space (2752x1536),
measured from full-resolution corner crops. Order: TL, TR, BR, BL.
"""
import sys
import cv2
import numpy as np

ROOT = 'spots/libertystone-one'
PLATE_SIZE = (2752, 1536)
SCREEN = np.float32([[1352, 566], [2456, 518], [2418, 1316], [1242, 1276]])
_RAW = cv2.imread(f'{ROOT}/dashboard/dashboard.png', cv2.IMREAD_COLOR)
# a real panel has a thin black border inside the bezel (deeper at the bottom chin);
# it also hides any sub-pixel tracking error at the edge
_PAD_T, _PAD_S, _PAD_B = 44, 44, 70
DASH = cv2.copyMakeBorder(_RAW, _PAD_T, _PAD_B, _PAD_S, _PAD_S, cv2.BORDER_CONSTANT, value=(12, 8, 5))


def composite(frame, quad, soften=0.0, glow=0.92):
    """Warp DASH into `quad` (4x2, frame pixels, TL TR BR BL) and blend it in."""
    h, w = frame.shape[:2]
    dh, dw = DASH.shape[:2]
    src = np.float32([[0, 0], [dw, 0], [dw, dh], [0, dh]])
    M = cv2.getPerspectiveTransform(src, np.float32(quad))
    warped = cv2.warpPerspective(DASH, M, (w, h), flags=cv2.INTER_AREA, borderValue=0)
    mask = cv2.warpPerspective(np.full((dh, dw), 255, np.uint8), M, (w, h), flags=cv2.INTER_LINEAR)
    # emissive panel: a touch dimmer than the source, a soft glass sheen from top left
    warped = cv2.convertScaleAbs(warped, alpha=glow, beta=0)
    yy, xx = np.mgrid[0:dh, 0:dw].astype(np.float32)
    sheen = np.clip(0.09 * (1.0 - (xx / dw * 0.8 + yy / dh * 0.6)), 0, 0.09)
    sheen = cv2.warpPerspective((sheen * 255).astype(np.uint8), M, (w, h))
    if soften > 0:
        warped = cv2.GaussianBlur(warped, (0, 0), soften)
    # feather the edge by one pixel so it sits behind the bezel, not on top of it
    m = cv2.GaussianBlur(mask, (0, 0), 0.8).astype(np.float32)[..., None] / 255.0
    out = frame.astype(np.float32) * (1 - m) + warped.astype(np.float32) * m
    out += sheen.astype(np.float32)[..., None] * m
    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == '__main__' and sys.argv[1:] == ['check']:
    plate = cv2.imread(f'{ROOT}/clips/plate-A.png')
    out = composite(plate, SCREEN)
    cv2.imwrite(f'{ROOT}/clips/plate-A-composited-v2.png', out)
    SC = sys.argv[2] if len(sys.argv) > 2 else '/tmp'
    print('wrote plate-A-composited-v2.png')

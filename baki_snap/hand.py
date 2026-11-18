"""Stylised, volume-shaded human hand doing a finger snap.

Fingers are 3D joint chains (palm facing the viewer, curl towards the viewer),
projected orthographically with a slight yaw so curled fingers foreshorten.
Every finger is drawn as capsules, its volume shading comes from a distance
transform (clay look). Pose 0 = pre-snap (thumb pressed on middle finger),
pose 1 = post-snap (middle finger slammed into the palm, thumb released).
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw

CW, CH = 900, 1300
OX, OY = 450, 880                          # palm centre on canvas
YAW = np.radians(-18)
SKIN = np.array([0.86, 0.64, 0.50], np.float32)
SKIN_D = np.array([0.45, 0.27, 0.20], np.float32)
SKIN_H = np.array([1.00, 0.87, 0.77], np.float32)

# base (x, y up, z towards viewer), segment lengths, width, splay (deg)
FINGERS = {
    "pinky": ((-112, 150, 0), (84, 56, 44), 46, -14),
    "ring": ((-45, 180, 0), (102, 70, 52), 52, -5),
    "middle": ((22, 190, 0), (114, 78, 58), 56, 3),
    "index": ((88, 172, 0), (104, 68, 52), 54, 10),
}
PRE = {"pinky": (78, 84, 62), "ring": (74, 86, 62), "middle": (55, 60, 45), "index": (16, 18, 12)}
POST = {"pinky": (82, 88, 66), "ring": (80, 90, 66), "middle": (92, 96, 70), "index": (24, 30, 18)}
THUMB_BASE = np.array([95.0, -40.0, 30.0])
THUMB_LEN = (125, 100, 78)
THUMB_W = 62


def norm(v):
    return v / np.linalg.norm(v)


def finger_pts(k, bends):
    base, lens, _, splay = FINGERS[k]
    s = np.radians(splay)
    pts = [np.array(base, float)]
    phi = 0.0
    for ln, b in zip(lens, bends):
        phi += np.radians(b)
        d = np.array([np.sin(s) * np.cos(phi), np.cos(s) * np.cos(phi), np.sin(phi)])
        pts.append(pts[-1] + d * ln)
    return pts


def rodrigues(v, axis, ang):
    axis = norm(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


def thumb_pts(target, d0, hint):
    j0 = THUMB_BASE
    j1 = j0 + norm(d0) * THUMB_LEN[0]
    l1, l2 = THUMB_LEN[1], THUMB_LEN[2]
    d = target - j1
    dist = np.clip(np.linalg.norm(d), 1, l1 + l2 - 0.5)
    a = np.arccos(np.clip((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist), -1, 1))
    axis = np.cross(d, hint)
    j2 = j1 + rodrigues(norm(d), axis, a) * l1
    j3 = j2 + norm(target - j2) * l2
    return [j0, j1, j2, j3]


def _pre_thumb():
    mid_tip = finger_pts("middle", PRE["middle"])[-1]
    return thumb_pts(mid_tip + np.array([4, -2, 10]), np.array([0.15, 0.85, 0.55]), np.array([0.6, -0.4, 0.6]))


def _post_thumb():
    j1 = THUMB_BASE + norm(np.array([0.5, 0.7, 0.4])) * THUMB_LEN[0]
    tgt = j1 + norm(np.array([0.55, 0.8, 0.25])) * (THUMB_LEN[1] + THUMB_LEN[2]) * 0.96
    return thumb_pts(tgt, np.array([0.5, 0.7, 0.4]), np.array([0.6, -0.4, 0.6]))


PRE_THUMB, POST_THUMB = _pre_thumb(), _post_thumb()


def to_screen(p):
    x = p[0] * np.cos(YAW) - p[2] * np.sin(YAW)
    z = p[0] * np.sin(YAW) + p[2] * np.cos(YAW)
    return np.array([OX + x, OY - p[1]]), z


def snap_point():
    return to_screen(finger_pts("middle", PRE["middle"])[-1])[0]


def _mask_capsules(pts2, width, taper=0.86):
    im = Image.new("L", (CW, CH), 0)
    d = ImageDraw.Draw(im)
    n = len(pts2) - 1
    for i in range(n):
        w0 = width * (1 - (1 - taper) * i / n)
        a, b = tuple(pts2[i]), tuple(pts2[i + 1])
        d.line([a, b], fill=255, width=int(w0))
        for p in (a, b):
            r = w0 / 2
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
    return np.asarray(im, np.uint8)


def _shade(mask):
    m = (mask > 127).astype(np.uint8)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    mx = max(float(dist.max()), 1.0)
    n = np.clip(dist / mx, 0, 1)
    M = np.float32([[1, 0, -mx * 0.22], [0, 1, -mx * 0.3]])
    lit = cv2.warpAffine(n, M, (CW, CH))
    c = SKIN_D + (SKIN - SKIN_D) * np.sqrt(n)[..., None]
    c = c + (SKIN_H - SKIN) * (np.clip(lit - n * 0.55, 0, 1) ** 2)[..., None]
    a = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 0.9)
    return c, a


def _over(dst_c, dst_a, c, a):
    a3 = a[..., None]
    return dst_c * (1 - a3) + c * a3, dst_a + a * (1 - dst_a)


def render_hand(p, squeeze=0.0):
    """(rgb, alpha) of the hand at pose p in [0, 1]; squeeze presses thumb + middle together."""
    parts = []
    for k in FINGERS:
        bends = np.array(PRE[k]) * (1 - p) + np.array(POST[k]) * p
        if k == "middle":
            bends = bends + np.array([0, 4, 3]) * squeeze
        pts = finger_pts(k, bends)
        scr = [to_screen(q) for q in pts]
        parts.append((np.mean([s[1] for s in scr]) + 10, [s[0] for s in scr], FINGERS[k][2], 0.86))
    tp = [a * (1 - p) + b * p for a, b in zip(PRE_THUMB, POST_THUMB)]
    tp[-1] = tp[-1] + np.array([-2, -3, -2]) * squeeze
    scr = [to_screen(q) for q in tp]
    parts.append((np.mean([s[1] for s in scr]) + 40, [s[0] for s in scr], THUMB_W, 0.8))

    col = np.zeros((CH, CW, 3), np.float32)
    alp = np.zeros((CH, CW), np.float32)
    # forearm + palm (z = 0 plane)
    poly = [(-150, 160), (130, 175), (165, 20), (150, -120), (90, -175), (-110, -175), (-160, -60)]
    pts2 = [tuple(to_screen(np.array([x, y, 0.0]))[0]) for x, y in poly]
    im = Image.new("L", (CW, CH), 0)
    d = ImageDraw.Draw(im)
    d.polygon(pts2, fill=255)
    fx0 = to_screen(np.array([-105.0, -140.0, 0]))[0]
    fx1 = to_screen(np.array([105.0, -140.0, 0]))[0]
    d.rounded_rectangle([fx0[0], fx0[1], fx1[0], CH + 80], 80, fill=255)
    pm = cv2.GaussianBlur(np.asarray(im), (0, 0), 10)
    pm = np.where(pm > 127, 255, 0).astype(np.uint8)
    c, a = _shade(pm)
    # palm crease lines
    cr = np.zeros((CH, CW), np.float32)
    for (x0, y0), (x1, y1) in (((-120, 95), (120, 60)), ((-90, 40), (110, 10)), ((60, 120), (40, -120))):
        p0, p1 = to_screen(np.array([x0, y0, 0.0]))[0], to_screen(np.array([x1, y1, 0.0]))[0]
        cv2.line(cr, tuple(map(int, p0)), tuple(map(int, p1)), 1.0, 4, cv2.LINE_AA)
    cr = cv2.GaussianBlur(cr, (0, 0), 2.5)[..., None] * 0.18
    c = c * (1 - cr)
    col, alp = _over(col, alp, c, a)
    for _, p2, w, taper in sorted(parts, key=lambda q: q[0]):
        c, a = _shade(_mask_capsules(p2, w, taper))
        col, alp = _over(col, alp, c, a)
    # sleeve with brand stripe
    sl = Image.new("L", (CW, CH), 0)
    sx0 = to_screen(np.array([-150.0, 0, 0]))[0][0]
    sx1 = to_screen(np.array([150.0, 0, 0]))[0][0]
    ImageDraw.Draw(sl).rounded_rectangle([sx0, OY + 230, sx1, CH + 80], 60, fill=255)
    sla = cv2.GaussianBlur(np.asarray(sl, np.float32) / 255, (0, 0), 1.2)
    ys = np.arange(CH)[:, None, None]
    slc = np.zeros((CH, CW, 3), np.float32) + np.array([0.06, 0.06, 0.07], np.float32)
    slc = slc + ((ys > OY + 270) & (ys < OY + 286)) * np.array([0.94, 0.47, 0.17], np.float32)
    col, alp = _over(col, alp, slc, sla)
    return np.clip(col, 0, 1), np.clip(alp, 0, 1)


if __name__ == "__main__":
    import sys
    bg = np.zeros((CH, CW, 3), np.float32) + 0.08
    ims = []
    for p in (0.0, 0.5, 1.0):
        c, a = render_hand(p)
        ims.append(bg * (1 - a[..., None]) + c * a[..., None])
    sp = snap_point()
    cv2.circle(ims[0], (int(sp[0]), int(sp[1])), 7, (0, 0, 1), -1)
    cv2.imwrite(sys.argv[1], (np.hstack(ims)[..., ::-1] * 255).astype(np.uint8))

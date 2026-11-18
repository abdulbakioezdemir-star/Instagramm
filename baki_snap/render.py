"""BAKI MOTIONS – "Snap" motion edit.

Hand snaps -> 3D ripples run out of frame and come back -> the logo bursts up
through the water -> light lines shoot out of the logo -> the camera follows
one line through 4 value points, each seen from a different camera angle
(above, below, side, front) -> pull back over the whole network -> end card.

1080x1920, 30 fps, 120 BPM (1 beat = 15 frames), 18 s = 540 frames.
"""
import subprocess
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

import hand

W, H = 1080, 1920
FPS, FPB, NFRAMES = 30, 15, 540
F = 1500.0
ORANGE = np.array([0.95, 0.48, 0.16], np.float32)
WARM = np.array([1.0, 0.78, 0.5], np.float32)
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
WATER_Y = -2.6
GRID_Y = -5.0

# ------------------------------------------------------------------ easing
def clamp01(x):
    return float(np.clip(x, 0, 1))


def ease(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def back(x, s=1.7):
    x = clamp01(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def mix(a, b, t):
    return a + (b - a) * t


def norm(v):
    return v / (np.linalg.norm(v) + 1e-9)


# ------------------------------------------------------------------ logo asset
def load_logo():
    img = np.asarray(Image.open("assets/profil_oben.png").convert("RGB"), np.float32) / 255
    cx, cy = 177, 605
    crop = img[cy - 130: cy + 130, cx - 130: cx + 130]
    big = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
    la = np.clip((big[..., 0] - big[..., 2] - 0.25) / 0.25, 0, 1)
    la = cv2.GaussianBlur(la, (0, 0), 1.6)
    la = np.clip((la - 0.5) * 2.2 + 0.5, 0, 1)
    ys, xs = np.nonzero(la > 0.05)
    return la[ys.min() - 20: ys.max() + 20, xs.min() - 20: xs.max() + 20].astype(np.float32)


LOGO = load_logo()


def face_grad(h, w, top, bot, spec=0.0, pos=0.5):
    g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    face = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    face = np.broadcast_to(face, (h, w, 3)).copy()
    if spec:
        xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
        ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        face += np.exp(-((xs + ys * 0.5 - pos * 1.5) / 0.08) ** 2)[..., None] * spec
    return np.clip(face, 0, 1.2)


_tc = {}


def label_image(num, word):
    key = (num, word)
    if key in _tc:
        return _tc[key]
    S = 2
    fb = ImageFont.truetype(FONT_BLACK, 150 * S)
    fs = ImageFont.truetype(FONT_BOLD, 54 * S)
    tw = int(fb.getlength(word)) + 80 * S
    im = Image.new("L", (tw, 300 * S), 0)
    col = Image.new("RGB", (tw, 300 * S), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((40 * S, 10 * S), num, font=fs, fill=255)
    d.rectangle([40 * S, 82 * S, 40 * S + 70 * S, 88 * S], fill=255)
    d.text((40 * S, 95 * S), word, font=fb, fill=255)
    dc = ImageDraw.Draw(col)
    dc.rectangle([0, 0, tw, 92 * S], fill=(242, 125, 45))
    m = np.asarray(im.resize((tw // S, 300), Image.LANCZOS), np.float32) / 255
    c = np.asarray(col.resize((tw // S, 300), Image.LANCZOS), np.float32) / 255
    ys, xs = np.nonzero(m > 0.02)
    sl = (slice(max(ys.min() - 12, 0), ys.max() + 12), slice(max(xs.min() - 12, 0), xs.max() + 12))
    m, c = m[sl], c[sl]
    g = np.linspace(1.0, 0.82, m.shape[0], dtype=np.float32)[:, None, None]
    c = c * g
    _tc[key] = (m, c)
    return m, c


def text_mask(text, size, font=FONT_BLACK, tracking=0):
    key = ("t", text, size, font, tracking)
    if key in _tc:
        return _tc[key]
    f = ImageFont.truetype(font, size)
    ws = [f.getlength(ch) for ch in text]
    im = Image.new("L", (int(sum(ws) + tracking * len(text) + size), int(size * 1.7)), 0)
    d = ImageDraw.Draw(im)
    x = size // 2
    for ch, w_ in zip(text, ws):
        d.text((x, size // 4), ch, font=f, fill=255)
        x += w_ + tracking
    m = np.asarray(im, np.float32) / 255
    ys, xs = np.nonzero(m > 0.01)
    m = m[max(ys.min() - 14, 0): ys.max() + 14, max(xs.min() - 14, 0): xs.max() + 14]
    _tc[key] = m
    return m


# ------------------------------------------------------------------ camera
class Cam:
    def __init__(self, pos, target, roll=0.0):
        self.c = np.asarray(pos, float)
        fwd = norm(np.asarray(target, float) - self.c)
        up = np.array([0.0, 1.0, 0.0])
        if abs(np.dot(fwd, up)) > 0.98:
            up = np.array([0.0, 0.0, 1.0])
        right = norm(np.cross(up, fwd))
        cup = np.cross(fwd, right)
        cr, sr = np.cos(roll), np.sin(roll)
        self.r = right * cr + cup * sr
        self.u = cup * cr - right * sr
        self.f = fwd

    def to_cam(self, P):
        d = np.asarray(P, float) - self.c
        return np.stack([d @ self.r, -(d @ self.u), d @ self.f], -1)

    def project(self, P):
        q = self.to_cam(P)
        z = q[..., 2]
        zs = np.maximum(z, 1e-3)
        return np.stack([F * q[..., 0] / zs + W / 2, F * q[..., 1] / zs + H / 2], -1), z


def world_plane(frame, cam, mask, face, center, R, D, width, depth=0.0, side=(0.5, 0.2, 0.05), opacity=1.0,
                slices=14, glow=0.3, shadow=True):
    """Draw an image as an (optionally extruded) plane in world space."""
    if opacity <= 0.002:
        return frame
    h, w = mask.shape
    hgt = width * h / w
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    back_n = -norm(np.cross(R, D))
    corners = np.array([center - R * width / 2 - D * hgt / 2, center + R * width / 2 - D * hgt / 2,
                        center + R * width / 2 + D * hgt / 2, center - R * width / 2 + D * hgt / 2])

    def warp(img, off, interp=cv2.INTER_LINEAR):
        p, z = cam.project(corners + back_n * off)
        if np.any(z < 0.3):
            return None
        M = cv2.getPerspectiveTransform(src, p.astype(np.float32))
        return cv2.warpPerspective(img, M, (W, H), flags=interp)

    side = np.array(side, np.float32)
    if depth > 0:
        n = slices
        for k in range(n, 0, -1):
            a = warp(mask, depth * k / n)
            if a is None:
                continue
            a = a[..., None] * opacity
            frame = frame * (1 - a) + side * (0.45 + 0.55 * (1 - k / n)) * a
    a = warp(mask, 0)
    if a is None:
        return frame
    a = a[..., None] * opacity
    fc = warp(face, 0)
    frame = frame * (1 - a) + fc * a
    if glow:
        frame = frame + cv2.GaussianBlur(a, (0, 0), 28)[..., None] * ORANGE * glow
    return frame


# ------------------------------------------------------------------ main path (Catmull-Rom)
CTRL = np.array([[0, 0, 0], [0, 0, 2.2], [3.6, 1.4, 8.0], [-3.2, -1.6, 15.0], [4.2, 2.0, 22.0],
                 [-0.5, 0.4, 29.0], [-1.5, -0.5, 34.0], [-2.0, -1.0, 37.0]], float)


def catmull(P, n_per=300):
    pts = []
    P = np.vstack([P[0], P, P[-1]])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t = np.linspace(0, 1, n_per, endpoint=False)[:, None]
        pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    pts.append(P[-2][None])
    return np.vstack(pts)


PATH = catmull(CTRL)
SEG = np.linalg.norm(np.diff(PATH, axis=0), axis=1)
ARC = np.r_[0, np.cumsum(SEG)]
NODE_IDX = [2, 3, 4, 5]
NODE_S = [ARC[i * 300] for i in NODE_IDX]
NODES = [CTRL[i] for i in NODE_IDX]
S_END = ARC[-1]
LABELS = [("01", "VERTRAUEN"), ("02", "KREATIVITÄT"), ("03", "QUALITÄT"), ("04", "ERGEBNISSE")]
ARRIVE = [180, 270, 330, 390]
# arc-length keyframes of the line head: (frame, s)
HEAD_KEYS = [(118, 0.0), (180, NODE_S[0]), (212, NODE_S[0] + 0.3), (270, NODE_S[1]), (290, NODE_S[1] + 0.3),
             (330, NODE_S[2]), (348, NODE_S[2] + 0.3), (390, NODE_S[3]), (450, S_END)]


def keyed(keys, f, fn=ease_io):
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1:
            return mix(np.asarray(v0, float), np.asarray(v1, float), fn((f - f0) / (f1 - f0)))
    return keys[-1][1]


def point_at(s):
    s = np.clip(s, 0, S_END)
    i = int(np.clip(np.searchsorted(ARC, s) - 1, 0, len(SEG) - 1))
    t = (s - ARC[i]) / max(SEG[i], 1e-9)
    return PATH[i] + (PATH[i + 1] - PATH[i]) * t, norm(PATH[i + 1] - PATH[i])


# camera offset relative to the line head: (frame, offset xyz, roll)
CAM_KEYS = [(150, (-2.5, 1.5, -6.5)), (180, (1.2, 7.8, -3.2)), (210, (2.8, 6.6, 0.8)),        # 01 von oben
            (270, (-1.6, -7.2, -3.8)), (290, (-3.2, -5.8, 0.6)),                                # 02 von unten
            (330, (7.8, 0.6, -1.4)), (348, (6.4, 1.6, 2.2)),                                    # 03 von der Seite
            (390, (0.8, 1.2, 7.4)), (420, (-1.5, 2.2, 6.6))]                                    # 04 von vorne
ROLL_KEYS = [(150, 0.0), (180, 0.0), (210, 0.1), (270, 0.2), (290, 0.05), (330, -0.28), (348, -0.12), (390, 0.08), (420, 0.0)]


def cam_at(f):
    t = f / FPS
    # A) water + logo shot
    if f < 120:
        tilt = keyed([(0, 0.0), (30, 0.0), (58, 1.0), (82, 1.0), (102, 0.0)], f)
        pos = np.array([0.0, mix(0.2, 2.6, tilt), -9.5])
        tgt = np.array([0.0, mix(0.0, WATER_Y, tilt), mix(0.0, 2.0, tilt)])
        logo_cam = Cam(pos, tgt)
        return logo_cam
    logo_pos = np.array([0.0, 0.2, -9.5])
    logo_tgt = np.array([0.0, 0.0, 0.0])
    s = keyed(HEAD_KEYS, f)
    head, tan = point_at(s)
    off = keyed(CAM_KEYS, f)
    roll = keyed(ROLL_KEYS, f)
    chase_pos = head + np.asarray(off)
    chase_tgt = head + tan * 1.6
    for ns in NODE_S:                       # frame the value point + its label while we are there
        wn = float(np.exp(-((s - ns) / 1.6) ** 2))
        nd, _ = point_at(ns)
        chase_tgt = mix(chase_tgt, nd + np.array([0.0, 0.55, 0.0]), wn * 0.85)
    w = ease_io((f - 128) / 40)
    pos = mix(logo_pos, chase_pos, w)
    tgt = mix(logo_tgt, chase_tgt, w)
    # B) pull back over the whole network
    if f > 420:
        k = ease_io((f - 420) / 50)
        pos = mix(pos, np.array([-16.0, 13.0, 2.0]), k)
        tgt = mix(tgt, np.array([0.5, 0.0, 17.0]), k)
        roll = mix(roll, 0.0, k)
    return Cam(pos, tgt, roll)


# ------------------------------------------------------------------ background / planes
prng = np.random.default_rng(4)
STARS = np.c_[prng.uniform(-30, 30, 900), prng.uniform(-20, 22, 900), prng.uniform(-15, 50, 900)]
STAR_B = prng.uniform(0.3, 1.0, 900)
HW, HH = W // 2, H // 2
_py, _px = np.mgrid[0:HH, 0:HW].astype(np.float32)
_PX = (_px * 2 + 1 - W / 2)
_PY = (_py * 2 + 1 - H / 2)


def sky(cam):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    base = np.array([0.018, 0.02, 0.03], np.float32) * (1 - g) + np.array([0.04, 0.03, 0.03], np.float32) * g
    img = np.broadcast_to(base, (H, W, 3)).copy()
    # warm horizon glow (in the direction of +z, the logo)
    p, z = cam.project(np.array([[0.0, 0.0, 40.0]]))
    if z[0] > 0:
        yy, xx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32) * 8
        gl = np.exp(-((xx - p[0, 0]) ** 2 + (yy - p[0, 1]) ** 2) / (900.0 ** 2))
        img += cv2.resize(gl, (W, H))[..., None] * ORANGE * 0.12
    return img


def stars(img, cam, alpha=1.0):
    p, z = cam.project(STARS)
    ok = (z > 0.5) & (p[:, 0] > -20) & (p[:, 0] < W + 20) & (p[:, 1] > -20) & (p[:, 1] < H + 20)
    c = np.zeros((H, W), np.float32)
    for (x, y), zz, b in zip(p[ok], z[ok], STAR_B[ok]):
        r = max(1, int(28 / zz))
        cv2.circle(c, (int(x), int(y)), min(r, 6), float(b * min(1.0, 12 / zz)), -1, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 1.3)
    return img + c[..., None] * np.array([1.0, 0.8, 0.6], np.float32) * 0.6 * alpha


def ripple_height(r, t):
    """Height + slope of the water at radius r and time t (seconds)."""
    h = np.zeros_like(r)
    dh = np.zeros_like(r)
    def ring(front, amp, k=2.2, width=3.0, sign=1):
        nonlocal h, dh
        x = r - front
        env = np.exp(-(x / width) ** 2) * (x < width * 0.6)
        h += amp * env * np.sin(x * k * sign)
        dh += amp * env * np.cos(x * k * sign) * k
    if t > 1.0:                                   # snap: rings run outward and out of frame
        for i in range(3):
            tt = t - 1.0 - i * 0.16
            if tt > 0:
                ring(tt * 9.0, 0.32 * np.exp(-tt * 0.25), 2.4)
    if 2.2 < t < 3.05:                            # waves come back, carrying the logo
        tt = (3.0 - t) / 0.8
        for i in range(3):
            ring(max(tt * 18 - i * 1.2, 0), 0.45 * (1 - tt * 0.5), 2.0)
    if t > 3.0:                                   # burst crown
        tt = t - 3.0
        ring(tt * 7.0, 0.7 * np.exp(-tt * 0.9), 1.7)
        h += 0.9 * np.exp(-tt * 3) * np.exp(-(r / 1.2) ** 2)
    return h, dh


def water_and_grid(img, cam, t, water_amt, grid_amt):
    if water_amt <= 0.01 and grid_amt <= 0.01:
        return img
    dirs = (cam.r[None, None] * _PX[..., None] - cam.u[None, None] * _PY[..., None] + cam.f[None, None] * F)
    out = np.zeros((HH, HW, 3), np.float32)
    amask = np.zeros((HH, HW), np.float32)
    if water_amt > 0.01:
        dy = dirs[..., 1]
        tt = (WATER_Y - cam.c[1]) / np.where(np.abs(dy) < 1e-6, 1e-6, dy)
        ok = tt > 0
        x = cam.c[0] + dirs[..., 0] * tt
        z = cam.c[2] + dirs[..., 2] * tt
        dist = np.sqrt((x - cam.c[0]) ** 2 + (z - cam.c[2]) ** 2)
        r = np.sqrt(x * x + z * z)
        hgt, slope = ripple_height(r, t)
        # grid lines on the water, displaced by the waves (sells the 3D surface)
        gx = np.abs(((x + slope * 0.25 * x / (r + 1e-3)) % 1.0) - 0.5)
        gz = np.abs(((z + slope * 0.25 * z / (r + 1e-3)) % 1.0) - 0.5)
        fw = np.clip(dist * 0.004, 0.012, 0.06)
        lines = np.clip(1 - np.minimum(gx, gz) / fw, 0, 1) * np.exp(-dist * 0.06)
        crest = np.abs(slope) ** 1.2
        base = np.array([0.02, 0.025, 0.04], np.float32) + np.array([0.08, 0.05, 0.04], np.float32) * np.exp(-dist * 0.05)[..., None]
        col = base + ORANGE * (crest * 1.1)[..., None] + WARM * (lines * 0.3 + np.clip(hgt, 0, None) * 0.25)[..., None]
        fog = np.exp(-dist * 0.035)[..., None]
        col = col * fog + np.array([0.06, 0.04, 0.035], np.float32) * (1 - fog)
        out = np.where(ok[..., None], col, out)
        amask = np.maximum(amask, ok * water_amt)
    if grid_amt > 0.01:
        dy = dirs[..., 1]
        tt = (GRID_Y - cam.c[1]) / np.where(np.abs(dy) < 1e-6, 1e-6, dy)
        ok = tt > 0
        x = cam.c[0] + dirs[..., 0] * tt
        z = cam.c[2] + dirs[..., 2] * tt
        dist = np.linalg.norm(dirs * tt[..., None], axis=-1) / F * 1.0
        dist = np.sqrt((x - cam.c[0]) ** 2 + (z - cam.c[2]) ** 2 + (GRID_Y - cam.c[1]) ** 2)
        gx = np.abs(((x / 2) % 1.0) - 0.5)
        gz = np.abs(((z / 2) % 1.0) - 0.5)
        fw = np.clip(dist * 0.0025, 0.01, 0.05)
        lines = np.clip(1 - np.minimum(gx, gz) / fw, 0, 1) * np.exp(-dist * 0.045) * ok
        gcol = ORANGE * lines[..., None] * 0.55
        out = out * (1 - lines[..., None] * grid_amt) + gcol * grid_amt + out * 0
        amask = np.maximum(amask, lines * grid_amt)
        out = np.where((lines > 0)[..., None] & (amask < 1e-3)[..., None], gcol, out)
    up = cv2.resize(out, (W, H), interpolation=cv2.INTER_LINEAR)
    am = cv2.resize(amask, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    if water_amt > 0.01:
        return img * (1 - am) + up * am
    return img + up * grid_amt


# ------------------------------------------------------------------ lines
def bezier(p0, p1, p2, p3, n=120):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


lrng = np.random.default_rng(12)
SIDE_LINES = []
for i in range(9):                     # extra lines that burst out of the logo
    a = i / 9 * 2 * np.pi + 0.3
    d = np.array([np.cos(a), np.sin(a) * 0.8, 0.0])
    p0 = d * 1.6
    p3 = d * 14 + np.array([0, 0, lrng.uniform(6, 30)])
    SIDE_LINES.append(bezier(p0, d * 5, p3 - np.array([0, 0, 6]), p3))
NODE_BRANCHES = []
for n_i, nd in enumerate(NODES):
    br = []
    for j in range(3):
        a = lrng.uniform(0, 2 * np.pi)
        d = norm(np.array([np.cos(a), np.sin(a), lrng.uniform(-0.3, 0.6)]))
        br.append(bezier(nd, nd + d * 1.5, nd + d * 3.5 + np.array([0, 0, 1.5]), nd + d * 5 + np.array([0, 0, 3])))
    NODE_BRANCHES.append(br)


def draw_poly(canvas, cam, pts, frac, width=0.06, value=1.0):
    n = max(2, int(len(pts) * clamp01(frac)))
    if frac <= 0:
        return None
    p, z = cam.project(pts[:n])
    last = None
    for i in range(n - 1):
        if z[i] < 0.3 or z[i + 1] < 0.3:
            continue
        th = int(np.clip(F * width / ((z[i] + z[i + 1]) / 2), 1, 40))
        a, b = p[i], p[i + 1]
        if max(abs(a[0]), abs(b[0])) > 6 * W or max(abs(a[1]), abs(b[1])) > 6 * H:
            continue
        cv2.line(canvas, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), value, th, cv2.LINE_AA)
        last = (b, z[i + 1])
    return last


def glow_lines(img, canvas, strength=1.0):
    g1 = cv2.GaussianBlur(canvas, (0, 0), 6)
    g2 = cv2.GaussianBlur(canvas, (0, 0), 22)
    return img + (canvas[..., None] * WARM * 1.1 + g1[..., None] * ORANGE * 1.2 + g2[..., None] * ORANGE * 0.9) * strength


# ------------------------------------------------------------------ fx
def warp_scale(img, s, dx=0.0, dy=0.0, rot=0.0):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, s)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def zoom_burst(img, amount, cx=W / 2, cy=H / 2, n=8):
    if amount < 0.003:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        M = cv2.getRotationMatrix2D((cx, cy), 0, 1 + amount * i / (n - 1))
        acc += cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / n


def ring(img, cx, cy, radius, strength, thick=10):
    if strength < 0.01 or radius < 1:
        return img
    c = np.zeros((H, W), np.float32)
    cv2.circle(c, (int(cx), int(cy)), int(radius), 1.0, thick, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 5)
    return img + c[..., None] * ORANGE * 1.6 * strength


def spark(img, cx, cy, k):
    if k <= 0 or k >= 1:
        return img
    c = np.zeros((H, W), np.float32)
    for i in range(12):
        a = i / 12 * 2 * np.pi + 0.2
        r0 = 30 + 160 * ease(k)
        r1 = r0 + 70 * (1 - k)
        cv2.line(c, (int(cx + np.cos(a) * r0), int(cy + np.sin(a) * r0)), (int(cx + np.cos(a) * r1), int(cy + np.sin(a) * r1)), 1.0, 5, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 1.5) * (1 - k)
    return img + c[..., None] * WARM * 1.5


DROPS = np.random.default_rng(3)
DROP_V = np.c_[DROPS.normal(0, 2.2, 160), DROPS.uniform(4, 11, 160), DROPS.normal(0, 2.2, 160)]


def splash(img, cam, t0, t):
    dt = t - t0
    if dt < 0 or dt > 1.6:
        return img
    P = DROP_V * dt + np.array([0, -9.8, 0]) * 0.5 * dt * dt * 1.2
    P[:, 1] += WATER_Y
    alive = P[:, 1] > WATER_Y - 0.1
    p, z = cam.project(P[alive])
    c = np.zeros((H, W), np.float32)
    for (x, y), zz in zip(p, z):
        if zz > 0.5 and -50 < x < W + 50 and -50 < y < H + 50:
            cv2.circle(c, (int(x), int(y)), max(2, int(90 / zz)), 1.0, -1, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 2) * (1 - dt / 1.6)
    return img + c[..., None] * WARM * 0.9


# ------------------------------------------------------------------ frame
def logo_world(img, cam, f, t):
    """Logo position/rotation in world space (bursts out of the water at frame 90)."""
    if f < 88:
        return img
    k = (f - 88) / 26
    y = mix(WATER_Y - 2.0, 0.0, back(k, 1.2)) + 0.12 * np.sin(t * 2.2) * clamp01(k)
    spin = 3 * np.pi * (1 - ease((f - 88) / 34)) + 0.22 * np.sin(t * 1.3)
    R = np.array([np.cos(spin), 0.0, np.sin(spin)])
    D = np.array([0.0, -1.0, 0.0])
    width = mix(2.6, 4.2, ease(k))
    face = face_grad(LOGO.shape[0], LOGO.shape[1], (1.0, 0.64, 0.32), (0.9, 0.38, 0.1), 0.45, (np.sin(spin) * 0.5 + 0.5))
    return world_plane(img, cam, LOGO, face, np.array([0.0, y, 0.0]), R, D, width, depth=0.45,
                       side=(0.5, 0.18, 0.04), slices=18, glow=0.45)


def render(f):
    t = f / FPS
    cam = cam_at(f)
    img = sky(cam)
    img = stars(img, cam, alpha=0.4 + 0.6 * clamp01((f - 90) / 30))
    water_amt = 1.0 - clamp01((f - 150) / 30)
    grid_amt = clamp01((f - 140) / 40) * (1 - 0.5 * clamp01((f - 480) / 30))
    img = water_and_grid(img, cam, t, water_amt, grid_amt) if water_amt > 0.01 else water_and_grid(img, cam, t, 0, grid_amt)

    # --- lines (behind logo / labels)
    if f >= 118:
        canvas = np.zeros((H, W), np.float32)
        for i, ln in enumerate(SIDE_LINES):
            draw_poly(canvas, cam, ln, ease((f - 118 - i) / 30), 0.035, 0.75)
        s_head = keyed(HEAD_KEYS, f)
        n = int(np.searchsorted(ARC, s_head)) + 1
        last = draw_poly(canvas, cam, PATH[: max(n, 2)], 1.0, 0.07, 1.0)
        for ni, nd in enumerate(NODES):
            if f >= ARRIVE[ni]:
                for bi, br in enumerate(NODE_BRANCHES[ni]):
                    draw_poly(canvas, cam, br, ease((f - ARRIVE[ni] - bi * 3) / 25), 0.03, 0.6)
        img = glow_lines(img, canvas)
        head, _ = point_at(s_head)
        hp, hz = cam.project(head[None])
        if hz[0] > 0.3:
            r = int(np.clip(F * 0.12 / hz[0], 3, 60))
            img = ring(img, hp[0, 0], hp[0, 1], r, 1.0, -1)
    # --- nodes + labels
    for ni, nd in enumerate(NODES):
        if f < ARRIVE[ni] - 2:
            continue
        p, z = cam.project(nd[None])
        if z[0] > 0.3:
            r = F * 0.28 / z[0]
            pulse = np.exp(-(f - ARRIVE[ni]) / 6) if f >= ARRIVE[ni] else 0
            img = ring(img, p[0, 0], p[0, 1], r * (1 + 0.15 * np.sin(t * 4)), 0.8, max(3, int(r * 0.18)))
            img = ring(img, p[0, 0], p[0, 1], r * 0.35, 1.0, -1)
            if f >= ARRIVE[ni]:
                img = ring(img, p[0, 0], p[0, 1], r * (1 + 5 * ease((f - ARRIVE[ni]) / 14)), 1 - clamp01((f - ARRIVE[ni]) / 14), 6)
                img = img + 0.35 * pulse
        if f >= ARRIVE[ni]:
            ref = cam_at(ARRIVE[ni] + 12)                 # label faces the camera of its own shot
            k = back((f - ARRIVE[ni]) / 14, 1.5)
            m, c = label_image(*LABELS[ni])
            center = nd + ref.u * 1.15
            fade = 1 - clamp01((f - ARRIVE[ni] - 42) / 12)
            if fade > 0.01:
                img = world_plane(img, cam, m, c, center, ref.r, -ref.u, 3.0 * max(k, 0.01), depth=0.2,
                                  side=(0.55, 0.22, 0.06), slices=10, glow=0.15, opacity=fade)

    # --- logo
    if f < 300:
        img = logo_world(img, cam, f, t)
    else:
        img = logo_world(img, cam, f, t) if f > 420 else img
    img = splash(img, cam, 3.0, t)
    if 88 <= f < 104:
        lp, lz = cam.project(np.array([[0.0, WATER_Y, 0.0]]))
        img = ring(img, lp[0, 0], lp[0, 1], 40 + (f - 88) * 70, 1 - (f - 88) / 16, 14)
    if f >= 88:
        img = img + 0.9 * np.exp(-(f - 89) / 2.5) * (f >= 89)

    # --- hand snap (screen space)
    if f < 62:
        if f < 30:
            p_pose = 0.0
            squeeze = clamp01((f - 18) / 11)
        else:
            p_pose = min(1.0, (f - 30) / 3)
            squeeze = 0.0
        hc, ha = hand.render_hand(p_pose, squeeze)
        if 30 <= f < 33:                             # motion blur on the snap
            hc2, ha2 = hand.render_hand(max(0, p_pose - 0.33), 0)
            hc, ha = (hc + hc2) / 2, (ha + ha2) / 2
        sc = 1.25
        sp = hand.snap_point()
        rise = (1 - back(f / 22, 1.3)) * 1100
        drop = ease((f - 42) / 20) * 1500 if f > 42 else 0
        tx = W / 2 - sp[0] * sc
        ty = H * 0.42 - sp[1] * sc + rise + drop
        jitter = (np.random.default_rng(f).normal(0, 3, 2) * clamp01((f - 18) / 11)) if f < 30 else (0, 0)
        M = np.float32([[sc, 0, tx + jitter[0]], [0, sc, ty + jitter[1]]])
        hcw = cv2.warpAffine(hc, M, (W, H))
        haw = cv2.warpAffine(ha, M, (W, H))[..., None]
        # orange rim light from the snap
        rim = np.clip(haw[..., 0] - cv2.erode(haw[..., 0], np.ones((9, 9))), 0, 1)[..., None]
        img = img * (1 - haw) + hcw * haw + rim * ORANGE * (0.25 + 0.8 * np.exp(-max(0, f - 30) / 6) * (f >= 30))
        if f >= 30:
            cx, cy = W / 2, H * 0.42
            img = spark(img, cx, cy, (f - 30) / 10)
            img = ring(img, cx, cy, 30 + (f - 30) * 55, max(0, 1 - (f - 30) / 14), 8)
            img = img + 0.55 * np.exp(-(f - 30) / 2)
    if f < 8:
        img = img * (f / 8)

    # --- camera energy: shake on impacts, beat pulse, transitions
    sh = 10 * np.exp(-max(0, f - 30) / 4) * (f >= 30) + 18 * np.exp(-max(0, f - 89) / 5) * (f >= 89)
    for a in ARRIVE:
        sh += 7 * np.exp(-max(0, f - a) / 4) * (f >= a)
    rng = np.random.default_rng(f + 1000)
    pulse = 0.012 * np.exp(-((f % FPB) / FPB) * 6) if f >= 90 else 0
    img = warp_scale(img, 1 + pulse, *rng.normal(0, sh, 2))
    for a in ARRIVE[1:]:                                     # whip-blur while the camera swings between angles
        k = (f - (a - 14)) / 14
        if 0 <= k < 1:
            img = zoom_burst(img, 0.18 * np.sin(np.pi * k))

    # --- end card
    if f >= 470:
        k = ease_io((f - 470) / 16)
        img = img * (1 - 0.65 * k)
        img = zoom_burst(img, 0.3 * (1 - k)) if f < 486 else img
        from_logo = (f - 470)
        img = end_card(img, from_logo, t)
    if f >= 526:
        img = img * (1 - ease_io((f - 526) / 13))
    return np.clip(img, 0, 1)


def extrude2d(frame, mask, face, cx, cy, scale, rx, ry, depth, side, opacity=1.0, slices=14, glow=0.3):
    h, w = mask.shape
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

    def proj(z):
        P = np.c_[(src[:, 0] - w / 2) * scale, (src[:, 1] - h / 2) * scale, np.full(4, z)]
        cr, sr, cx_, sx_ = np.cos(ry), np.sin(ry), np.cos(rx), np.sin(rx)
        X = P[:, 0] * cr + P[:, 2] * sr
        Z = -P[:, 0] * sr + P[:, 2] * cr
        Y = P[:, 1] * cx_ - Z * sx_
        Z = P[:, 1] * sx_ + Z * cx_ + F
        return np.c_[F * X / Z + cx, F * Y / Z + cy].astype(np.float32)

    side = np.array(side, np.float32)
    for k in range(slices, 0, -1):
        a = cv2.warpPerspective(mask, cv2.getPerspectiveTransform(src, proj(depth * k / slices)), (W, H))[..., None] * opacity
        frame = frame * (1 - a) + side * (0.45 + 0.55 * (1 - k / slices)) * a
    M0 = cv2.getPerspectiveTransform(src, proj(0))
    a = cv2.warpPerspective(mask, M0, (W, H))[..., None] * opacity
    frame = frame * (1 - a) + cv2.warpPerspective(face, M0, (W, H)) * a
    return frame + cv2.GaussianBlur(a, (0, 0), 30)[..., None] * ORANGE * glow


def end_card(img, lf, t):
    k = back(lf / 22, 1.3)
    ry = 2 * np.pi * (1 - ease(lf / 28)) + 0.22 * np.sin(t * 1.4)
    face = face_grad(LOGO.shape[0], LOGO.shape[1], (1.0, 0.64, 0.32), (0.9, 0.38, 0.1), 0.45, np.sin(ry) * 0.5 + 0.5)
    img = extrude2d(img, LOGO, face, W / 2, 700 + 16 * np.sin(t * 2), 600 / LOGO.shape[1] * max(k, 0.01), 0.12, ry,
                    LOGO.shape[1] * 0.1, (0.5, 0.18, 0.04), glow=0.5)
    if lf >= 10:
        kk = back((lf - 10) / 14, 1.2)
        m = text_mask("BAKI MOTIONS", 120)
        fc = face_grad(m.shape[0], m.shape[1], (1, 1, 1), (0.85, 0.85, 0.9), 0.5, (lf - 10) / 30)
        img = extrude2d(img, m, fc, W / 2, 1120, mix(0.4, 1.0, kk), 0.14, mix(0.9, 0, kk), 34, (0.55, 0.22, 0.06),
                        opacity=clamp01((lf - 10) / 6), glow=0.15)
    if lf >= 20:
        a = ease((lf - 20) / 10)
        m = text_mask("@bakimotions", 50, FONT_BOLD, 2)
        h, w = m.shape
        y0, x0 = 1240, W // 2 - w // 2
        c = np.zeros((H, W), np.float32)
        c[y0:y0 + h, x0:x0 + w] = m
        img = img * (1 - c[..., None] * a) + np.array([0.98, 0.62, 0.32], np.float32) * c[..., None] * a
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/snap_raw.mp4"
    if len(sys.argv) > 2:
        for fr in map(int, sys.argv[2:]):
            cv2.imwrite(f"{out}_{fr:03d}.png", (render(fr)[..., ::-1] * 255).astype(np.uint8))
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(NFRAMES):
        p.stdin.write((render(f) * 255 + 0.5).astype(np.uint8).tobytes())
        if f % 30 == 0:
            print("frame", f, flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()

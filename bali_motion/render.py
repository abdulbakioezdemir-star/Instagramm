"""Bali motion edit – procedural 3D scenes, beat-synced transitions.

1080x1920, 30 fps, 120 BPM -> 1 beat = 15 frames, 1 bar = 60 frames, 16 s.
Raw (ungraded) frames are piped into ffmpeg -> out/bali_raw.mp4.
"""
import subprocess
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
RW, RH = 720, 1280            # internal scene resolution (upscaled)
FPS, FPB = 30, 15
NFRAMES = 480
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

yy, xx = np.mgrid[0:RH, 0:RW].astype(np.float32)
U = (xx - RW / 2) / RH
V = (yy - RH / 2) / RH


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a + (b - a) * t


def col(*c):
    return np.array(c, np.float32)


def sky(hz, top, mid, low, curve=1.0):
    k = np.clip((hz - V) / (hz + 0.5), 0, 1) ** curve
    k = k[..., None]
    c1 = mix(low, mid, np.clip(k * 2, 0, 1))
    return mix(c1, top, np.clip(k * 2 - 1, 0, 1))


def sun(img, su, sv, r, c, glow=1.0):
    d = np.sqrt((U - su) ** 2 + (V - sv) ** 2)
    disk = sstep(r, r * 0.92, d)[..., None]
    g = (np.exp(-d / (r * 1.5)) * 0.8 + np.exp(-d / (r * 6)) * 0.35)[..., None] * glow
    return img + c * g + disk * (col(1, .97, .9) - img) * 0.95


def water(t, hz, camh, speed, deep, refl, su, sunc, sway=0.0):
    dv = np.maximum(V - hz, 1e-4)
    z = camh / dv
    x = U * z + sway
    tz = z + t * speed
    damp = np.exp(-z * 0.04)
    w1 = np.sin(x * 1.3 + tz * 0.9)
    w2 = np.sin(x * 0.7 - tz * 1.7 + 1.3)
    w3 = np.sin(x * 2.9 + tz * 2.3 + t * 2)
    w4 = np.sin(x * 9 + tz * 7 + t * 3) + 0.6 * np.sin(x * 15 - tz * 11 + 2)
    fine = np.exp(-z * 0.6)
    slope = (np.cos(x * 1.3 + tz * 0.9) * 0.6 + np.cos(x * 2.9 + tz * 2.3 + t * 2) * 0.4) * damp + w4 * fine * 0.5
    fres = np.clip(1 - dv * 3.2, 0, 1)[..., None] ** 1.5
    base = mix(deep, refl, fres)
    base = base * (1 + 0.25 * slope[..., None])
    width = 0.015 + dv * 0.55
    col_mask = np.exp(-((U - su) / width) ** 2)
    sparkle = np.clip((w1 * 0.5 + w3 * 0.5 + w2 * 0.3 + w4 * fine * 0.6) * 0.5 + 0.5, 0, 1) ** 6
    glit = (col_mask * (0.25 + sparkle * 2.2 * damp + 0.2))[..., None]
    out = base + sunc * glit
    fog = np.exp(-dv * 22)[..., None]
    out = mix(out, refl * 1.05, fog * 0.8)
    return out, (V > hz)[..., None]


# ------------------------------------------------------------------ scenes
def scene_ocean(t):
    """Golden sunset sea with Tanah Lot sea temple on its rock."""
    hz = -0.06
    img = sky(hz, col(.10, .09, .26), col(.85, .38, .32), col(1.0, .72, .38), 0.8)
    su, sv = 0.10, hz - 0.055 + 0.004 * t
    img = sun(img, su, sv, 0.045, col(1.0, .6, .25))
    # clouds: soft horizontal bands
    cl = np.sin(U * 9 + t * 0.15 + np.sin(V * 40) * 0.6) * np.sin(V * 55 + U * 3)
    cl = np.clip(cl, 0, 1) * sstep(hz - 0.02, hz - 0.35, V) * sstep(hz - 0.45, hz - 0.2, V)
    img = mix(img, col(1.0, .55, .45), cl[..., None] * 0.35)
    wat, wm = water(t, hz, 0.06, 3.0, col(.03, .10, .16), col(.95, .55, .38), su, col(1.0, .7, .35))
    img = np.where(wm, wat, img)
    # Tanah Lot rock silhouette (moves with parallax)
    c = -0.15 - t * 0.010
    base = hz + 0.012
    w = 0.085
    q = (U - c) / w
    prof = base - 0.055 * np.sqrt(np.clip(1 - q ** 2, 0, 1)) ** 0.7 - 0.006 * np.sin(U * 140) * (np.abs(q) < 1)
    rock = (np.abs(q) < 1) & (V > prof) & (V < base)
    # meru tiers on top
    top = base - 0.055
    for i in range(5):
        tw = 0.018 - i * 0.003
        y0 = top - i * 0.008
        tier = (np.abs(U - c) < tw) & (V > y0 - 0.008) & (V < y0)
        rock |= tier
    trees = (np.abs(q) < 0.9) & (V > prof - 0.012 * (0.5 + 0.5 * np.sin(U * 260) ** 2)) & (V < base)
    rock |= trees
    rim = np.exp(-np.abs(V - prof) * 120) * np.clip(1 - np.abs(U - su) * 2, 0, 1)
    rc = col(.05, .025, .05) + col(.9, .4, .15)[None, None] * rim[..., None] * 0.6
    img = np.where(rock[..., None], rc, img)
    # reflection of rock
    vr = 2 * base - V
    qr = (U + 0.003 * np.sin(V * 300 + t * 6) - c) / w
    profr = base - 0.055 * np.sqrt(np.clip(1 - qr ** 2, 0, 1)) ** 0.7
    refl = (np.abs(qr) < 1) & (vr > profr) & (V > base) & (V < base + 0.05)
    img = np.where(refl[..., None], img * 0.45, img)
    return img


def scene_rice(t):
    """Morning flight over Tegallalang-style rice terraces, volcano behind."""
    hz = -0.13
    img = sky(hz, col(.25, .48, .85), col(.65, .78, .92), col(1.0, .86, .62), 0.9)
    img = sun(img, -0.22, hz - 0.12, 0.03, col(1.0, .8, .5), 0.8)
    # volcano Agung
    pk = 0.08
    sl = np.abs(U - pk)
    vol = V > (hz - 0.17 + 0.9 * sl ** 1.25 + 0.004 * np.sin(U * 90))
    img = np.where((vol & (V < hz + 0.01))[..., None], mix(col(.42, .52, .70), col(.80, .80, .85), np.clip((hz - V) * 4, 0, 1)[..., None] * 0) * (0.85 + 0.3 * np.clip(0.5 - (U - pk) * 3, 0, 1))[..., None], img)
    # ground plane
    camh = 0.12
    dv = np.maximum(V - hz, 1e-4)
    z = camh / dv
    x = U * z + 1.5 * np.sin(t * 0.4)
    tz = z + t * 2.6
    f = tz * 3.2 + 1.6 * np.sin(x * 1.4 + 0.8 * np.sin(tz * 0.9)) + 0.6 * np.sin(x * 3.3 + 1.0)
    idx = np.floor(f)
    band = f - idx
    h = np.sin(idx * 12.9898) * 43758.5453
    h = h - np.floor(h)
    lime = col(.58, .82, .22)
    deep = col(.12, .42, .10)
    g = mix(deep, lime, h[..., None])
    shade = (0.7 + 0.5 * band)[..., None]
    dike = (sstep(0.0, 0.07, band) * sstep(1.0, 0.9, band))[..., None]
    gc = g * shade * (0.45 + 0.55 * dike)
    flooded = (h > 0.82)[..., None]
    gc = np.where(flooded, mix(gc, col(.9, .85, .7), 0.45 * dike), gc)
    # palm dots on dikes
    palms = (np.sin(x * 9.1) * np.sin(idx * 7.3) > 0.9) & (band > 0.86) & (z < 3)
    gc = np.where(palms[..., None], col(.05, .2, .05), gc)
    far = np.clip(z / 6, 0, 1)[..., None]
    gc = mix(gc, mix(deep, lime, 0.5) * 0.85, far)
    fog = np.exp(-dv * 9)[..., None]
    gc = mix(gc, col(.82, .86, .82), fog * 0.85)
    img = np.where((V > hz)[..., None], gc, img)
    # light morning haze
    return img


def _gate_mask():
    """Candi Bentar (split gate) silhouette, drawn once."""
    S = 1400
    im = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(im)
    gap = 70
    ground = 1200
    tiers = [(330, 120), (300, 150), (270, 60), (250, 110), (215, 50), (190, 95), (160, 45), (130, 85), (100, 40), (70, 70), (40, 60)]
    for side in (-1, 1):
        y = ground
        for w, h in tiers:
            x0 = S / 2 + side * gap / 2
            x1 = x0 + side * w
            d.rectangle([min(x0, x1), y - h, max(x0, x1), y], fill=255)
            # cornice
            d.rectangle([min(x0, x1 + side * 12), y - h - 6, max(x0, x1 + side * 12), y - h + 4], fill=255)
            y -= h
        # finial spikes
        xm = S / 2 + side * (gap / 2 + 20)
        d.polygon([(xm - 14, y), (xm + 14, y), (xm, y - 60)], fill=255)
        # side ornaments
        for k in range(6):
            yy_ = ground - 160 - k * 140
            xo = S / 2 + side * (gap / 2 + tiers[min(k * 2, len(tiers) - 1)][0] + 14)
            d.polygon([(xo, yy_), (xo + side * 26, yy_ - 30), (xo, yy_ - 60)], fill=255)
    # stairs
    for k in range(6):
        d.rectangle([S / 2 - 260 + k * 22, ground + k * 22, S / 2 + 260 - k * 22, ground + 22 + k * 22], fill=255)
    return np.asarray(im, np.float32) / 255


GATE = _gate_mask()


def scene_temple(t, push=0.12):
    """Sunset behind the Gates of Heaven, dolly push-in, god rays."""
    hz = 0.17
    img = sky(hz, col(.12, .08, .30), col(.95, .45, .30), col(1.0, .80, .45), 0.7)
    su, sv = 0.0, hz - 0.30
    ang = np.arctan2(V - sv, U - su)
    rays = (np.sin(ang * 34 + t * 0.4) * 0.5 + 0.5) ** 3 * np.exp(-np.sqrt((U - su) ** 2 + (V - sv) ** 2) * 3)
    img = img + col(1.0, .7, .4) * rays[..., None] * 0.35
    img = sun(img, su, sv, 0.05, col(1.0, .55, .25), 1.2)
    # far mountains / clouds sea
    mt = V > hz - 0.06 + 0.03 * np.sin(U * 7 + 1) + 0.015 * np.sin(U * 23)
    img = np.where(mt[..., None], mix(img, col(.55, .32, .42), 0.6), img)
    # gate (2D sprite warped = dolly push-in)
    s = (RH * 0.95 / GATE.shape[0]) * (1 + push * t)
    M = np.array([[s, 0, RW / 2 - s * GATE.shape[1] / 2], [0, s, RH * 0.98 - s * 1200 * 0.98 - (1 - push * t * 0.3) * 40]], np.float32)
    m = cv2.warpAffine(GATE, M, (RW, RH))[..., None]
    rim = cv2.GaussianBlur(m[..., 0], (0, 0), 3)
    edge = np.clip(rim - m[..., 0] * 0.9, 0, 1)[..., None]
    img = img * (1 - m) + col(.05, .02, .04) * m + col(1.0, .6, .3) * edge * 0.8
    # reflecting pool
    floor = V > hz + 0.22
    refl = img[::-1]
    refl = np.roll(refl, int(RH * 0.0) , 0)
    rip = (np.sin(V * 400 + t * 5) * 2).astype(np.int32)
    refl = np.take_along_axis(refl, np.clip(xx.astype(np.int32) + rip, 0, RW - 1)[..., None].repeat(3, 2), 1)
    img = np.where(floor[..., None], refl * col(.55, .5, .6) + 0.02, img)
    return img


def _palm_sprite():
    S = 900
    im = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(im)
    # trunk: curved, tapering
    pts = [(450 + 60 * np.sin(k / 30 * 1.6) ** 2 * 1.5, 900 - k * 18) for k in range(31)]
    for i in range(30):
        w = int(26 - i * 0.55)
        d.line([pts[i], pts[i + 1]], fill=255, width=w)
    top = pts[-1]
    rng = np.random.default_rng(3)
    for a in np.linspace(-2.9, -0.25, 9):
        L_ = rng.uniform(230, 320)
        spine = []
        for k in range(26):
            s = k / 25
            ang = a + (s ** 1.6) * 1.1 * np.sign(np.cos(a) + 1e-3) * 0.9
            x = top[0] + np.cos(a) * L_ * s
            y = top[1] + np.sin(a) * L_ * s + (s ** 2) * L_ * 0.55
            spine.append((x, y))
        d.line(spine, fill=255, width=7)
        for k in range(3, 25):
            x, y = spine[k]
            lx = 55 * (1 - k / 26)
            d.line([(x, y), (x + lx * 0.6, y + lx)], fill=255, width=4)
            d.line([(x, y), (x - lx * 0.6, y + lx)], fill=255, width=4)
    return np.asarray(im, np.float32) / 255


PALM = _palm_sprite()


def scene_palms(t):
    """Blue-hour beach, three depth layers of palms (3D parallax truck)."""
    hz = 0.05
    img = sky(hz, col(.06, .10, .32), col(.55, .30, .55), col(1.0, .55, .35), 0.75)
    su = 0.05
    img = sun(img, su, hz - 0.02, 0.05, col(1.0, .45, .2), 1.1)
    wat, wm = water(t, hz, 0.05, 1.2, col(.03, .06, .15), col(.85, .45, .45), su, col(1.0, .55, .3))
    img = np.where(wm, wat, img)
    # sand
    sand = V > 0.36 + 0.02 * np.sin(U * 6 + 1)
    img = np.where(sand[..., None], col(.10, .06, .08), img)
    layers = [(0.35, 0.05, 4, 0.0, col(.12, .06, .16)), (0.65, 0.12, 3, 0.4, col(.06, .03, .08)), (1.25, 0.32, 2, 1.0, col(.01, .01, .02))]
    for scale, speed, n, blur, c in layers:
        for i in range(n):
            s = RH * scale / PALM.shape[0]
            span = RW * 1.6
            px = ((i / n * span - t * speed * RH * 1.0 + scale * 300) % span) - RW * 0.3
            py = RH * (0.42 + 0.25 * scale) - s * 900
            flip = -1 if (i + int(scale * 10)) % 2 else 1
            M = np.array([[s * flip, 0, px + (s * 900 if flip < 0 else 0) - s * 450], [0, s, py]], np.float32)
            m = cv2.warpAffine(PALM, M, (RW, RH))
            if blur > 0.5:
                m = cv2.GaussianBlur(m, (0, 0), 4)
            m = m[..., None]
            img = img * (1 - m) + c * m
    return img


SCENES = {"ocean": scene_ocean, "rice": scene_rice, "temple": scene_temple, "palms": scene_palms}


def render_scene(name, t):
    img = SCENES[name](t)
    img = np.clip(img, 0, 1.5)
    return cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)


# ------------------------------------------------------------- typography
_cache = {}


def text_mask(text, size, font=FONT_BLACK, tracking=0):
    key = (text, size, font, tracking)
    if key in _cache:
        return _cache[key]
    f = ImageFont.truetype(font, size)
    widths = [f.getbbox(ch)[2] for ch in text]
    tw = sum(widths) + tracking * (len(text) - 1)
    pad = size // 2
    im = Image.new("L", (int(tw + 2 * pad), int(size * 1.5 + 2 * pad)), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for ch, w in zip(text, widths):
        d.text((x, pad), ch, font=f, fill=255)
        x += w + tracking
    m = np.asarray(im, np.float32) / 255
    ys, xs = np.nonzero(m > 0.01)
    m = m[max(ys.min() - 20, 0): ys.max() + 20, max(xs.min() - 20, 0): xs.max() + 20]
    _cache[key] = m
    return m


def title3d(frame, text, size, cx, cy, ry=0.0, rx=0.0, dist=1.0, depth=40, alpha=1.0,
            face_top=(1.0, .93, .70), face_bot=(1.0, .62, .25), side=(.45, .18, .08)):
    """Real 3D extruded text: each depth slice is projected with its own homography."""
    if alpha <= 0.001:
        return frame
    m = text_mask(text, size)
    h, w = m.shape
    f = 1400.0
    D = f * dist
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    cr, sr = np.cos(ry), np.sin(ry)
    cxr, sxr = np.cos(rx), np.sin(rx)
    nslices = 18

    def proj(zoff):
        P = np.c_[corners[:, 0] - w / 2, corners[:, 1] - h / 2, np.full(4, zoff)]
        X = P[:, 0] * cr + P[:, 2] * sr
        Z = -P[:, 0] * sr + P[:, 2] * cr
        Y = P[:, 1] * cxr - Z * sxr
        Z = P[:, 1] * sxr + Z * cxr
        Z = Z + D
        return np.c_[f * X / Z + cx, f * Y / Z + cy].astype(np.float32)

    out = frame
    grad = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    face = (np.array(face_top, np.float32) * (1 - grad) + np.array(face_bot, np.float32) * grad)
    face = np.broadcast_to(face, (h, w, 3)).copy()
    # shadow / glow
    Hm = cv2.getPerspectiveTransform(corners, proj(depth * 1.2) + np.float32([18, 30]))
    sh = cv2.warpPerspective(m, Hm, (W, H))
    sh = cv2.GaussianBlur(sh, (0, 0), 18)[..., None]
    out = out * (1 - sh * 0.55 * alpha)
    for k in range(nslices, 0, -1):
        z = depth * k / nslices
        Hk = cv2.getPerspectiveTransform(corners, proj(z))
        mk = cv2.warpPerspective(m, Hk, (W, H))[..., None] * alpha
        shade = 0.55 + 0.45 * (1 - k / nslices)
        out = out * (1 - mk) + np.array(side, np.float32) * shade * mk
    H0 = cv2.getPerspectiveTransform(corners, proj(0))
    m0 = cv2.warpPerspective(m, H0, (W, H))[..., None] * alpha
    fc = cv2.warpPerspective(face, H0, (W, H))
    out = out * (1 - m0) + fc * m0
    glow = cv2.GaussianBlur(m0, (0, 0), 25)
    if glow.ndim == 2:
        glow = glow[..., None]
    out = out + glow * np.array([1.0, .6, .3], np.float32) * 0.35
    return out


def subtitle(frame, text, cy, alpha, size=44, tracking=18, slide=0.0, color=(1, .97, .92)):
    if alpha <= 0.001:
        return frame
    m = text_mask(text, size, FONT_SEMI, tracking)
    h, w = m.shape
    x0 = int(W / 2 - w / 2 + slide)
    y0 = int(cy - h / 2)
    canvas = np.zeros((H, W), np.float32)
    xs0, ys0 = max(x0, 0), max(y0, 0)
    xs1, ys1 = min(x0 + w, W), min(y0 + h, H)
    if xs1 <= xs0 or ys1 <= ys0:
        return frame
    canvas[ys0:ys1, xs0:xs1] = m[ys0 - y0: ys1 - y0, xs0 - x0: xs1 - x0]
    sh = cv2.GaussianBlur(canvas, (0, 0), 6)[..., None]
    frame = frame * (1 - sh * 0.5 * alpha)
    c = canvas[..., None] * alpha
    return frame * (1 - c) + np.array(color, np.float32) * c


# ------------------------------------------------------------ transitions
def warp_scale(img, s, cx=W / 2, cy=H / 2, rot=0.0, dx=0.0, dy=0.0):
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def zoom_burst(img, amount, n=8):
    if amount < 0.002:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        acc += warp_scale(img, 1 + amount * i / (n - 1))
    return acc / n


def whip(img, shift, blur):
    img = np.roll(img, int(shift), axis=1)
    k = int(max(1, blur))
    return cv2.blur(img, (k, 1)) if k > 1 else img


def flip3d(img, angle):
    """Rotate the frame around the vertical axis (card flip)."""
    f = 1600.0
    c, s = np.cos(angle), np.sin(angle)
    src = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    dst = []
    for x, y in src:
        X, Y = x - W / 2, y - H / 2
        Xr, Zr = X * c, X * s + f
        dst.append([f * Xr / Zr + W / 2, f * Y / Zr + H / 2])
    Hm = cv2.getPerspectiveTransform(src, np.float32(dst))
    return cv2.warpPerspective(img, Hm, (W, H))


def rgb_split(img, px):
    if px < 0.5:
        return img
    p = int(px)
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], -p, 1)
    out[..., 2] = np.roll(img[..., 2], p, 1)
    return out


def beat_env(f, start=0, every=FPB, decay=0.25):
    if f < start:
        return 0.0
    dt = ((f - start) % every) / FPS
    return float(np.exp(-dt / decay * 3))


# -------------------------------------------------------------- timeline
DROP_CUTS = [240, 255, 270, 285, 300, 308, 315, 323, 330, 338, 345, 353]   # beat / half-beat
DROP_SEQ = [("palms", 1.0, "SUNSET"), ("ocean", 6.0, "OCEAN"), ("rice", 3.0, "JUNGLE"), ("temple", 1.5, "TEMPLES"),
            ("palms", 3.5, "SURF"), ("ocean", 2.0, "SPIRIT"), ("rice", 5.5, "GREEN"), ("temple", 0.5, "GODS"),
            ("palms", 2.5, "WAVES"), ("ocean", 4.0, "GOLD"), ("rice", 1.0, "LIFE"), ("temple", 2.5, "BALI")]


def ease_out_back(x, s=1.7):
    x = np.clip(x, 0, 1) - 1
    return x * x * ((s + 1) * x + s) + 1


def render(f):
    t = f / FPS
    # ---------------- bar 1-2: ocean + 3D title
    if f < 120:
        img = render_scene("ocean", t)
        expo = sstep(0, 24, f)
        img = img * expo
        # title flies in from depth on frame 30 (beat 3)
        if f >= 6:
            k = (f - 6) / 24
            dist = mix(6.0, 1.0, ease_out_back(k, 1.2)) if f < 30 else 1.0
            ry = mix(1.2, 0.0, ease_out_back(k, 1.4)) if f < 30 else 0.18 * np.sin((f - 30) / 40)
            rx = 0.12 + 0.05 * np.sin(f / 25)
            if f >= 108:                              # fly into camera
                q = (f - 108) / 12
                dist = mix(1.0, 0.12, q ** 2)
            img = title3d(img, "BALI", 330, W / 2, H * 0.36, ry=ry, rx=rx, dist=dist, depth=70, alpha=min(1, (f - 6) / 8))
        if 45 <= f < 110:
            a = sstep(45, 55, f) * (1 - sstep(100, 108, f))
            img = subtitle(img, "ISLAND OF THE GODS", H * 0.47, a, slide=(1 - sstep(45, 60, f)) * 80)
        # beat pulse from title slam
        pulse = 0.05 * beat_env(f, 30, 1000, 0.4) if f >= 30 else 0
        img = warp_scale(img, 1 + pulse)
        img = img + 0.6 * np.exp(-(f - 30) / 3) * (f >= 30)          # flash on slam
        # whip-out into rice (cut on frame 120)
        if f >= 114:
            q = (f - 114) / 6
            img = whip(img, -q ** 2 * W * 0.6, 1 + q * 120)
    # ---------------- bar 3: rice terraces
    elif f < 180:
        img = render_scene("rice", (f - 120) / FPS + 0.5)
        if f < 126:
            q = 1 - (f - 120) / 6
            img = whip(img, q ** 2 * W * 0.6, 1 + q * 120)
        a = sstep(128, 138, f) * (1 - sstep(168, 174, f))
        img = subtitle(img, "UBUD", H * 0.70, a, size=92, tracking=40, slide=(1 - sstep(128, 142, f)) * -60)
        img = subtitle(img, "RICE TERRACES", H * 0.745, a, size=36, tracking=14)
        img = warp_scale(img, 1 + 0.02 * beat_env(f, 120) + (f - 120) * 0.0008)
        if f >= 172:                                       # flip out
            img = flip3d(img, (f - 172) / 8 * np.pi / 2)
    # ---------------- bar 4: temple build-up
    elif f < 240:
        lt = (f - 180) / FPS
        img = render_scene("temple", lt)
        if f < 188:
            img = flip3d(img, -(1 - (f - 180) / 8) * np.pi / 2)
        a = sstep(190, 200, f) * (1 - sstep(226, 232, f))
        img = subtitle(img, "GATES OF HEAVEN", H * 0.80, a, size=54, tracking=20)
        build = sstep(186, 236, f)
        rng = np.random.default_rng(f)
        sx, sy = rng.normal(0, 14 * build ** 2, 2)
        img = warp_scale(img, 1 + 0.03 * build + 0.025 * beat_env(f, 180, FPB // (2 if f > 210 else 1)), dx=sx, dy=sy)
        img = rgb_split(img, 10 * build ** 3)
        if f >= 236:                                       # 4 frames of darkness before the drop
            img = img * 0.0
    # ---------------- bar 5-6: DROP – fast beat cuts
    elif f < 360:
        i = max(k for k, c in enumerate(DROP_CUTS) if c <= f)
        c0 = DROP_CUTS[i]
        c1 = DROP_CUTS[i + 1] if i + 1 < len(DROP_CUTS) else 360
        name, off, word = DROP_SEQ[i]
        local = (f - c0) / FPS
        img = render_scene(name, off + local * 1.5)
        since = f - c0
        burst = 0.35 * np.exp(-since / 2.5)
        img = zoom_burst(img, burst)
        img = warp_scale(img, 1.06 + 0.06 * np.exp(-since / 4) - 0.002 * since, rot=(-1) ** i * 2.0 * np.exp(-since / 4))
        img = rgb_split(img, 18 * np.exp(-since / 2))
        img = img + 0.5 * np.exp(-since / 1.5)
        if i == 0:
            img = title3d(img, "BALI", 360, W / 2, H * 0.45, ry=0.25 * np.sin(since / 6), rx=0.15,
                          dist=mix(0.55, 1.0, ease_out_back(since / 10)), depth=90)
        else:
            sc = ease_out_back(min(1, since / 5))
            img = title3d(img, word, 170 if len(word) < 6 else 140, W / 2, H * 0.5, ry=(-1) ** i * 0.35 * (1 - sc) + (-1) ** i * 0.15,
                          rx=0.2, dist=mix(2.5, 1.0, sc), depth=45, alpha=min(1, since / 2 + 0.3))
        if c1 - f <= 2:                                    # pre-cut smear
            img = zoom_burst(img, 0.15 * (3 - (c1 - f)))
    # ---------------- bar 7: palms breakdown
    elif f < 420:
        img = render_scene("palms", (f - 360) / FPS + 4)
        if f < 368:
            img = zoom_burst(img, 0.4 * (1 - (f - 360) / 8))
            img = img + 0.6 * (1 - (f - 360) / 8)
        a = sstep(370, 382, f) * (1 - sstep(410, 416, f))
        img = subtitle(img, "SELAMAT DATANG", H * 0.30, a, size=60, tracking=22, slide=(1 - sstep(370, 386, f)) * 70)
        img = warp_scale(img, 1.04 + (f - 360) * 0.0012 + 0.025 * beat_env(f, 360))
        if f >= 414:
            img = zoom_burst(img, 0.5 * ((f - 414) / 6) ** 2)
    # ---------------- bar 8: final hero
    else:
        img = render_scene("temple", 0.8 + (f - 420) / FPS * 0.6)
        since = f - 420
        if since < 8:
            img = zoom_burst(img, 0.5 * (1 - since / 8))
        img = img + 0.7 * np.exp(-since / 2)
        k = since / 18
        img = title3d(img, "BALI", 330, W / 2, H * 0.19, ry=mix(-0.9, 0.0, ease_out_back(k, 1.3)) + 0.1 * np.sin(since / 20),
                      rx=0.14, dist=mix(3.0, 1.0, ease_out_back(k, 1.1)), depth=70)
        a = sstep(432, 442, f)
        img = subtitle(img, "INDONESIA", H * 0.265, a, size=48, tracking=34)
        img = warp_scale(img, 1 + 0.02 * beat_env(f, 420) + since * 0.0006)
        img = img * (1 - sstep(462, 479, f))
    return np.clip(img, 0, 1)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/bali_raw.mp4"
    frames = range(NFRAMES)
    if len(sys.argv) > 2:                                   # preview single frames
        for fr in map(int, sys.argv[2:]):
            img = render(fr)
            cv2.imwrite(f"{out}_{fr:03d}.png", (img[..., ::-1] * 255).astype(np.uint8))
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in frames:
        img = render(f)
        p.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())
        if f % 30 == 0:
            print("frame", f, flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()

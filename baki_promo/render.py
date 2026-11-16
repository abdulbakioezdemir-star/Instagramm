"""BAKI MOTIONS promo – 3D motion edit built from the Instagram profile screenshots.

1080x1920, 30 fps, 120 BPM (1 beat = 15 frames), 16 s.
Scenes: profile push-in -> logo bursts out of the avatar and spins in 3D ->
floating glass service cards -> reels pop out of the profile grid -> CTA.
"""
import subprocess
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS, FPB, NFRAMES = 30, 15, 480
F = 1600.0                                  # focal length for 3D projection
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
ORANGE = np.array([0.94, 0.47, 0.17], np.float32)


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), np.float32) / 255


def sharpen(img, amt=0.35):
    return np.clip(img + (img - cv2.GaussianBlur(img, (0, 0), 1.2)) * amt, 0, 1)


def blur_region(img, y0, y1, sigma=38):
    out = img.copy()
    reg = cv2.GaussianBlur(img[y0:y1], (0, 0), sigma) * 0.8
    m = np.ones((y1 - y0, 1, 1), np.float32)
    fade = 25
    m[:fade, 0, 0] = np.linspace(0, 1, fade)
    m[-fade:, 0, 0] = np.linspace(1, 0, fade)
    out[y0:y1] = img[y0:y1] * (1 - m) + reg * m
    return out


def round_alpha(h, w, r):
    a = Image.new("L", (w, h), 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return np.asarray(a, np.float32) / 255


# ------------------------------------------------------------------ assets
SHOT_A = sharpen(load("assets/profil_oben.png"))
SHOT_B = sharpen(load("assets/profil_posts.png"))
# privacy: blur the "suggested accounts" row (third-party profile photo/name)
SHOT_A = blur_region(SHOT_A, 1575, 2185)
SHOT_B = blur_region(SHOT_B, 990, 1598)
IH, IW = SHOT_A.shape[:2]
AV_C, AV_R = np.array([177.0, 605.0]), 128.0          # avatar centre/radius in screenshot px
SHOT_ALPHA = round_alpha(IH, IW, 70)

# Logo: cut the orange mark out of the avatar, upscale 4x, rebuild clean edges
crop = SHOT_A[int(AV_C[1] - 130): int(AV_C[1] + 130), int(AV_C[0] - 130): int(AV_C[0] + 130)]
big = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
orangeness = big[..., 0] - big[..., 2]
la = np.clip((orangeness - 0.25) / 0.25, 0, 1)
la = cv2.GaussianBlur(la, (0, 0), 1.6)
la = np.clip((la - 0.5) * 2.2 + 0.5, 0, 1)
ys, xs = np.nonzero(la > 0.05)
pad = 24
LOGO_A = la[ys.min() - pad: ys.max() + pad, xs.min() - pad: xs.max() + pad].astype(np.float32)
LH, LW = LOGO_A.shape
LOGO_FRAC = (xs.max() - xs.min()) / 4 / (2 * AV_R)     # logo width relative to avatar diameter
LOGO_OFF = np.array([(xs.min() + xs.max()) / 8 - 130, (ys.min() + ys.max()) / 8 - 130])  # offset from avatar centre
# avatar without the logo (for after it has flown out)
SHOT_A_EMPTY = SHOT_A.copy()
yy_, xx_ = np.mgrid[0:IH, 0:IW]
d = np.sqrt((xx_ - AV_C[0]) ** 2 + (yy_ - AV_C[1]) ** 2)
hole = (d < AV_R - 6) & ~((xx_ > 225) & (yy_ > 650))     # keep the "+" badge
SHOT_A_EMPTY[hole] = SHOT_A_EMPTY[hole] * 0 + 0.97

# Reel thumbnails from the grid (above the view counters)
THUMBS = []
for x0, x1 in ((0, 388), (392, 778)):
    t = SHOT_B[1772:2195, x0:x1]
    t = sharpen(cv2.resize(t, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_LANCZOS4), 0.4)
    THUMBS.append((t, round_alpha(t.shape[0], t.shape[1], 36), ((x0 + x1) / 2, (1772 + 2195) / 2), (x1 - x0)))


# ------------------------------------------------------------------ helpers
def ease(x):
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def back(x, s=1.7):
    x = np.clip(x, 0, 1) - 1
    return x * x * ((s + 1) * x + s) + 1


def mix(a, b, t):
    return a + (b - a) * t


def beat_env(f, start=0, every=FPB, k=6.0):
    if f < start:
        return 0.0
    return float(np.exp(-((f - start) % every) / every * k))


def rot(rx, ry, rz):
    cz, sz, cy, sy, cx, sx = np.cos(rz), np.sin(rz), np.cos(ry), np.sin(ry), np.cos(rx), np.sin(rx)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    return Rx @ Ry @ Rz


def project(pts, w, h, cx, cy, scale, rx=0, ry=0, rz=0, z=0.0):
    """Project image-space points of a w*h plane placed in 3D."""
    pts = np.asarray(pts, np.float64)
    P = np.c_[(pts[:, 0] - w / 2) * scale, (pts[:, 1] - h / 2) * scale, np.full(len(pts), z)]
    P = P @ rot(rx, ry, rz).T
    Z = P[:, 2] + F
    return np.c_[F * P[:, 0] / Z + cx, F * P[:, 1] / Z + cy].astype(np.float32)


def place(frame, rgb, alpha, cx, cy, scale, rx=0, ry=0, rz=0, opacity=1.0, shadow=0.6, glow=0.0, z=0.0, frost=None):
    if opacity <= 0.002:
        return frame
    h, w = alpha.shape
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = project(src, w, h, cx, cy, scale, rx, ry, rz, z)
    M = cv2.getPerspectiveTransform(src, dst)
    a = cv2.warpPerspective(alpha, M, (W, H)) * opacity
    if shadow > 0:
        sh = cv2.GaussianBlur(np.roll(a, 40, 0), (0, 0), 30)
        frame = frame * (1 - sh[..., None] * shadow)
    if glow > 0:
        g = cv2.GaussianBlur(a, (0, 0), 35)[..., None]
        frame = frame + g * ORANGE * glow
    a3 = a[..., None]
    if frost is not None:
        frame = frame * (1 - a3) + frost * a3
    c = cv2.warpPerspective(rgb * alpha[..., None], M, (W, H)) * opacity
    return frame * (1 - a3) + c


# ------------------------------------------------------------------ background
_gy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
BG_BASE = mix(np.array([0.025, 0.028, 0.040], np.float32), np.array([0.055, 0.035, 0.030], np.float32), _gy)
BG_BASE = np.broadcast_to(BG_BASE, (H, W, 3)).copy()
sy_, sx_ = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32) * 8
prng = np.random.default_rng(5)
PARTS = np.c_[prng.uniform(0, W, 140), prng.uniform(0, H, 140), prng.uniform(0.3, 1.0, 140), prng.uniform(0, 6.28, 140)]


def background(t, energy=1.0):
    img = BG_BASE.copy()
    small = np.zeros((H // 8, W // 8), np.float32)
    for (gx, gy, r, sp, ph) in ((0.2, 0.25, 520, 0.3, 0), (0.85, 0.7, 600, 0.25, 2), (0.5, 0.95, 700, 0.2, 4)):
        cx = W * gx + 120 * np.sin(t * sp + ph)
        cy = H * gy + 90 * np.cos(t * sp * 1.3 + ph)
        small += np.exp(-((sx_ - cx) ** 2 + (sy_ - cy) ** 2) / (r * r))
    glow = cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC)[..., None]
    img = img + glow * ORANGE * 0.18 * energy
    # perspective grid floor (3D)
    canvas = np.zeros((H, W), np.float32)
    hz = H * 0.62
    for k in range(-14, 15):
        x_far = W / 2 + k * 30
        x_near = W / 2 + k * 260
        cv2.line(canvas, (int(x_far), int(hz)), (int(x_near), H), 1.0, 2, cv2.LINE_AA)
    for k in range(12):
        zz = ((k + (t * 1.2) % 1) / 12)
        y = hz + (H - hz) * zz ** 2.2
        cv2.line(canvas, (0, int(y)), (W, int(y)), 1.0, 2, cv2.LINE_AA)
    fadeg = np.clip((np.arange(H) - hz) / (H - hz), 0, 1)[:, None] ** 1.2
    img = img + (canvas * fadeg)[..., None] * ORANGE * 0.12
    # floating bokeh particles (parallax by depth)
    pc = np.zeros((H, W), np.float32)
    for x, y, zd, ph in PARTS:
        py = (y - t * 60 * zd) % H
        px = x + 25 * np.sin(t * 0.8 + ph)
        cv2.circle(pc, (int(px), int(py)), int(1 + 4 * zd), float(0.4 + 0.6 * zd), -1, cv2.LINE_AA)
    pc = cv2.GaussianBlur(pc, (0, 0), 2.0)
    img = img + pc[..., None] * np.array([1.0, 0.75, 0.5], np.float32) * 0.35
    return img


# ------------------------------------------------------------------ text
_tc = {}


def text_mask(text, size, font=FONT_BLACK, tracking=0):
    key = (text, size, font, tracking)
    if key in _tc:
        return _tc[key]
    f = ImageFont.truetype(font, size)
    ws = [f.getlength(ch) for ch in text]
    tw = sum(ws) + tracking * (len(text) - 1)
    p = size // 2
    im = Image.new("L", (int(tw + 2 * p), int(size * 1.6 + 2 * p)), 0)
    dr = ImageDraw.Draw(im)
    x = p
    for ch, w_ in zip(text, ws):
        dr.text((x, p), ch, font=f, fill=255)
        x += w_ + tracking
    m = np.asarray(im, np.float32) / 255
    ys, xs = np.nonzero(m > 0.01)
    m = m[max(ys.min() - 16, 0): ys.max() + 16, max(xs.min() - 16, 0): xs.max() + 16]
    _tc[key] = m
    return m


def extrude(frame, mask, face, cx, cy, scale, rx, ry, rz=0.0, depth=40, side=(0.45, 0.17, 0.05), opacity=1.0, slices=16, glow=0.3):
    """True 3D extrusion: every depth slice gets its own perspective projection."""
    if opacity <= 0.002:
        return frame
    h, w = mask.shape
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    Ms = cv2.getPerspectiveTransform(src, project(src, w, h, cx + 25, cy + 45, scale, rx, ry, rz, depth))
    sh = cv2.GaussianBlur(cv2.warpPerspective(mask, Ms, (W, H)), (0, 0), 22)[..., None]
    frame = frame * (1 - sh * 0.5 * opacity)
    side = np.array(side, np.float32)
    for k in range(slices, 0, -1):
        M = cv2.getPerspectiveTransform(src, project(src, w, h, cx, cy, scale, rx, ry, rz, depth * k / slices))
        a = cv2.warpPerspective(mask, M, (W, H))[..., None] * opacity
        frame = frame * (1 - a) + side * (0.5 + 0.5 * (1 - k / slices)) * a
    M0 = cv2.getPerspectiveTransform(src, project(src, w, h, cx, cy, scale, rx, ry, rz, 0))
    a = cv2.warpPerspective(mask, M0, (W, H))[..., None] * opacity
    fc = cv2.warpPerspective(face, M0, (W, H))
    frame = frame * (1 - a) + fc * a
    if glow:
        frame = frame + cv2.GaussianBlur(a, (0, 0), 30)[..., None] * ORANGE * glow
    return frame


def face_grad(h, w, top, bot, spec=0.0, spec_pos=0.5):
    g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    face = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    face = np.broadcast_to(face, (h, w, 3)).copy()
    if spec > 0:
        xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
        ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        band = np.exp(-((xs + ys * 0.5 - spec_pos * 1.5) / 0.08) ** 2)[..., None]
        face = face + band * spec
    return np.clip(face, 0, 1.2)


def title(frame, text, size, cx, cy, rx=0.0, ry=0.0, dist=1.0, opacity=1.0, depth=30,
          top=(1, 1, 1), bot=(0.86, 0.86, 0.9), side=(0.55, 0.22, 0.06), font=FONT_BLACK, spec_pos=None):
    m = text_mask(text, size, font)
    f = face_grad(m.shape[0], m.shape[1], top, bot, 0.5 if spec_pos is not None else 0, spec_pos or 0)
    return extrude(frame, m, f, cx, cy, 1.0 / dist, rx, ry, 0, depth, side, opacity, 12, 0.15)


def flat_text(frame, text, cy, opacity, size=40, tracking=10, font=FONT_SEMI, color=(0.92, 0.92, 0.95), dx=0.0):
    if opacity <= 0.002:
        return frame
    m = text_mask(text, size, font, tracking)
    h, w = m.shape
    x0, y0 = int(W / 2 - w / 2 + dx), int(cy - h / 2)
    xs0, ys0, xs1, ys1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xs1 <= xs0 or ys1 <= ys0:
        return frame
    c = np.zeros((H, W), np.float32)
    c[ys0:ys1, xs0:xs1] = m[ys0 - y0: ys1 - y0, xs0 - x0: xs1 - x0]
    c = c[..., None] * opacity
    return frame * (1 - c) + np.array(color, np.float32) * c


def logo3d(frame, cx, cy, width, rx, ry, rz=0.0, opacity=1.0, glow=0.35):
    s = width / LW
    spec = (np.sin(ry * 1.0 + 0.6) * 0.5 + 0.5)
    face = face_grad(LH, LW, (1.0, 0.62, 0.30), (0.90, 0.38, 0.10), 0.45, spec)
    return extrude(frame, LOGO_A, face, cx, cy, s, rx, ry, rz, depth=LW * 0.10, side=(0.50, 0.18, 0.04),
                   opacity=opacity, slices=18, glow=glow)


# ------------------------------------------------------------------ glass cards
def star(dr, cx, cy, r, fill):
    pts = []
    for i in range(8):
        a = i * np.pi / 4 - np.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    dr.polygon(pts, fill=fill)


def make_card(title_, sub, w=880, h=210):
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w * S - 1, h * S - 1], 46 * S, fill=(26, 26, 34, 205), outline=(240, 125, 50, 255), width=3 * S)
    dr.rounded_rectangle([6 * S, 6 * S, w * S - 6 * S, 40 * S], 40 * S, fill=(255, 255, 255, 18))
    icx, icy = 110 * S, h * S // 2
    dr.ellipse([icx - 62 * S, icy - 62 * S, icx + 62 * S, icy + 62 * S], fill=(240, 120, 44, 255))
    star(dr, icx, icy, 38 * S, (255, 255, 255, 255))
    dr.text((205 * S, 50 * S), title_, font=ImageFont.truetype(FONT_BOLD, 58 * S), fill=(255, 255, 255, 255))
    dr.text((207 * S, 125 * S), sub, font=ImageFont.truetype(FONT_SEMI, 32 * S), fill=(190, 190, 200, 255))
    im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    return a[..., :3].copy(), a[..., 3].copy()


CARDS = [make_card("Animierte Reels", "3D & Motion Design, das stoppt"),
         make_card("Werbefilme", "Für Marken, Produkte & Events"),
         make_card("Account-Management", "Content, Planung & Wachstum")]


def make_button(text, w=700, h=150):
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w * S - 1, h * S - 1], h * S // 2, fill=(240, 120, 44, 255))
    dr.rounded_rectangle([10 * S, 8 * S, w * S - 10 * S, h * S // 2], h * S // 3, fill=(255, 255, 255, 40))
    f = ImageFont.truetype(FONT_BOLD, 54 * S)
    tw = f.getlength(text)
    dr.text(((w * S - tw) / 2, h * S / 2 - 36 * S), text, font=f, fill=(255, 255, 255, 255))
    im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    return a[..., :3].copy(), a[..., 3].copy()


BUTTON = make_button("Jetzt DM schreiben")


# ------------------------------------------------------------------ effects
def warp_scale(img, s, cx=W / 2, cy=H / 2, rot_=0.0, dx=0.0, dy=0.0):
    M = cv2.getRotationMatrix2D((cx, cy), rot_, s)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def zoom_burst(img, amount, n=8, cx=W / 2, cy=H / 2):
    if amount < 0.003:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        acc += warp_scale(img, 1 + amount * i / (n - 1), cx, cy)
    return acc / n


def rgb_split(img, px):
    p = int(px)
    if p < 1:
        return img
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], -p, 1)
    out[..., 2] = np.roll(img[..., 2], p, 1)
    return out


def shockwave(img, cx, cy, radius, strength):
    if strength < 0.01:
        return img
    c = np.zeros((H, W), np.float32)
    cv2.circle(c, (int(cx), int(cy)), int(radius), 1.0, 10, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 6)
    return img + c[..., None] * ORANGE * 1.6 * strength


BURST = np.random.default_rng(9).uniform(0, 2 * np.pi, (60, 2))


def particle_burst(img, cx, cy, k):
    if k <= 0 or k >= 1:
        return img
    c = np.zeros((H, W), np.float32)
    for ang, spd in BURST:
        r0 = 40 + 700 * ease(k) * (0.4 + spd / 6.28)
        r1 = r0 + 90 * (1 - k)
        p0 = (int(cx + np.cos(ang) * r0), int(cy + np.sin(ang) * r0))
        p1 = (int(cx + np.cos(ang) * r1), int(cy + np.sin(ang) * r1))
        cv2.line(c, p0, p1, 1.0, 4, cv2.LINE_AA)
    c = cv2.GaussianBlur(c, (0, 0), 1.5) * (1 - k)
    return img + c[..., None] * np.array([1.0, 0.7, 0.4], np.float32) * 1.2


# ------------------------------------------------------------------ timeline
S0 = W / IW                                   # screenshot fills the width
AV_SCREEN = AV_C * S0                         # avatar on screen at f=0 (top aligned)


def page_state_s1(f):
    """Scene 1: page scales around the avatar (camera pushes into the profile picture)."""
    z = 1 + 0.35 * ease_io(f / 60)
    scale = S0 * z
    centre = AV_SCREEN + (np.array([IW / 2, IH / 2]) - AV_C) * scale
    return centre, scale


def render(f):
    t = f / FPS
    img = background(t)

    # ---------------- 0-60: Instagram profile, push-in to the avatar
    if f < 150:
        if f < 60:
            (cx, cy), sc = page_state_s1(f)
            rx = ry = 0.0
            dim = 1.0
        else:
            (c0x, c0y), s0 = page_state_s1(60)
            k = ease_io((f - 60) / 26)
            cx = mix(c0x, W / 2, k)
            cy = mix(c0y, H * 0.86, k) + 14 * np.sin(t * 2.0) * k
            sc = mix(s0, 0.38, k)
            rx = mix(0.0, 0.62, k)
            ry = mix(0.0, -0.18, k) + 0.05 * np.sin(t * 1.3) * k
            dim = mix(1.0, 0.45, k)
        shot = SHOT_A if f < 60 else SHOT_A_EMPTY
        img = place(img, shot * dim, SHOT_ALPHA, cx, cy, sc, rx, ry, opacity=1.0, shadow=0.7 if f >= 60 else 0, glow=0.25 if f >= 60 else 0)
        # avatar on screen (for pulse + logo start)
        av = project([AV_C], IW, IH, cx, cy, sc, rx, ry)[0]
        if 28 <= f < 60:                                    # story-ring pulse on beat 3
            k = (f - 28) / 32
            img = shockwave(img, av[0], av[1], AV_R * sc * (1.05 + 0.6 * k), (1 - k) * 0.9)
            img = shockwave(img, av[0], av[1], AV_R * sc * 1.05, 0.5 + 0.5 * np.sin(f * 0.6))
        if f < 10:
            img = img * (f / 10)
        # logo bursts out at frame 60 (bar 2, drop)
        if f >= 60:
            k = (f - 60) / 36
            e = back(min(1, k), 1.3)
            (c0x, c0y), s0 = page_state_s1(60)
            start = AV_SCREEN + LOGO_OFF * s0
            w0 = LOGO_FRAC * 2 * AV_R * s0
            lx = mix(start[0], W / 2, e)
            ly = mix(start[1], H * 0.33, e) + 22 * np.sin(t * 2.2) * min(1, k)
            lw = mix(w0, 620, e)
            spin = 4 * np.pi * (1 - ease(min(1, (f - 60) / 40)))
            ry_l = spin + 0.28 * np.sin(t * 1.4) * min(1, k)
            rx_l = 0.12 * np.sin(t * 1.1) * min(1, k) + 0.1
            img = particle_burst(img, start[0], start[1], (f - 60) / 22)
            img = shockwave(img, start[0], start[1], 60 + (f - 60) * 45, max(0, 1 - (f - 60) / 16))
            img = logo3d(img, lx, ly, lw, rx_l, ry_l, opacity=1.0)
            img = img + 0.8 * np.exp(-(f - 60) / 2.5)
        if f >= 90:                                         # name slams in on beat
            k = (f - 90) / 14
            img = title(img, "BAKI MOTIONS", 118, W / 2, H * 0.535 + 8 * np.sin(t * 2.0), rx=0.15,
                        ry=mix(1.1, 0.0, back(k, 1.2)) + 0.05 * np.sin(t), dist=mix(2.6, 1.0, back(k, 1.1)),
                        opacity=min(1, k * 2), depth=34, spec_pos=(f - 90) / 40)
        if f >= 105:
            k = ease((f - 105) / 12)
            img = flat_text(img, "SOCIAL MEDIA AGENTUR", H * 0.595, k, 40, 16, dx=(1 - k) * 80, color=(0.96, 0.62, 0.35))
        # shake on drop and on name slam
        sh = 14 * np.exp(-(f - 60) / 5) * (f >= 60) + 8 * np.exp(-(f - 90) / 4) * (f >= 90)
        rng = np.random.default_rng(f)
        img = warp_scale(img, 1 + 0.015 * beat_env(f, 60), dx=rng.normal(0, sh), dy=rng.normal(0, sh))
        if f >= 142:
            img = zoom_burst(img, 0.5 * ((f - 142) / 8) ** 2)
            img = img + 0.4 * ((f - 142) / 8) ** 3

    # ---------------- 150-270: services – floating glass cards
    elif f < 270:
        lt = f - 150
        img = logo3d(img, W / 2, 300 + 12 * np.sin(t * 2), 300, 0.12, t * 1.6, opacity=min(1, lt / 6), glow=0.3)
        k = ease(lt / 12)
        img = flat_text(img, "UNSERE LEISTUNGEN", 540, k * (1 - ease((f - 246) / 10)), 46, 18, FONT_BOLD, dx=(1 - k) * -90)
        frost = cv2.GaussianBlur(img, (0, 0), 18) * 0.55 + 0.03
        for i, (rgb, a) in enumerate(CARDS):
            st = 150 + i * 30
            if f < st:
                continue
            kk = (f - st) / 14
            e = back(min(1, kk), 1.4)
            side = -1 if i % 2 else 1
            cx = mix(W / 2 + side * 1000, W / 2, e)
            cy = 780 + i * 260 + 14 * np.sin(t * 2.0 + i * 1.7)
            ry = mix(side * -1.3, 0.0, e) + 0.12 * np.sin(t * 1.3 + i)
            rx = 0.18 + 0.05 * np.sin(t * 1.1 + i * 2)
            sc = 1.0 + 0.04 * beat_env(f, st, FPB * 2)
            op = 1.0
            if f >= 240 + i * 3:                             # fly out
                ko = ease((f - 240 - i * 3) / 14)
                cy -= ko * 900
                ry += side * ko * 1.5
                op = 1 - ko
            img = place(img, rgb, a, cx, cy, sc, rx, ry, opacity=min(1, kk * 3) * op, shadow=0.5, glow=0.25, frost=frost)
        if lt < 8:
            img = zoom_burst(img, 0.5 * (1 - lt / 8))
            img = img + 0.4 * (1 - lt / 8)
        img = warp_scale(img, 1.0 + 0.012 * beat_env(f, 150))
        if f >= 262:
            img = zoom_burst(img, 0.5 * ((f - 262) / 8) ** 2)

    # ---------------- 270-390: portfolio – reels pop out of the profile grid
    elif f < 390:
        lt = f - 270
        k = back(min(1, lt / 18), 1.2)
        pcx, pcy = W / 2, mix(H * 1.4, H * 0.66, k) + 16 * np.sin(t * 1.8)
        psc = 0.50
        prx = mix(1.1, 0.30, k) + 0.04 * np.sin(t * 1.2)
        pry = 0.22 * np.sin(t * 0.9)
        popped = [f >= 285, f >= 300]
        dim = 1.0 - 0.4 * ease((f - 285) / 15) if f >= 285 else 1.0
        img = place(img, SHOT_B * dim, SHOT_ALPHA, pcx, pcy, psc, prx, pry, shadow=0.7, glow=0.3)
        targets = [(300, 760), (780, 860)]
        for i, (thumb, ta, (tx, ty), tw) in enumerate(THUMBS):
            st = 285 + i * 15
            if f < st:
                continue
            kk = (f - st) / 16
            e = back(min(1, kk), 1.3)
            sp = project([(tx, ty)], IW, IH, pcx, pcy, psc, prx, pry)[0]
            s_start = psc * tw / thumb.shape[1]
            cx = mix(sp[0], targets[i][0], e)
            cy = mix(sp[1], targets[i][1], e) + 18 * np.sin(t * 2.1 + i * 2) * min(1, kk)
            sc = mix(s_start, 0.66, e) * (1 + 0.035 * beat_env(f, st, FPB * 2))
            rx = mix(prx, 0.08, e) + 0.05 * np.sin(t * 1.4 + i)
            ry = mix(pry, (0.32 if i == 0 else -0.32), e) + 0.08 * np.sin(t * 1.1 + i * 3)
            rz = mix(0, (-0.06 if i == 0 else 0.06), e)
            img = place(img, thumb, ta, cx, cy, sc, rx, ry, rz, shadow=0.7, glow=0.45)
            img = shockwave(img, sp[0], sp[1], 30 + (f - st) * 30, max(0, 1 - (f - st) / 12) * 0.7)
        if f >= 300:
            kt = ease((f - 300) / 12)
            img = title(img, "UNSERE ARBEITEN", 96, W / 2, 300, rx=0.12, ry=mix(-0.9, 0, back((f - 300) / 14)) + 0.04 * np.sin(t),
                        opacity=kt, depth=26, spec_pos=(f - 300) / 40)
            img = flat_text(img, "Reels, die Aufmerksamkeit holen", 400, kt, 40, 2, FONT_SEMI, (0.96, 0.62, 0.35))
        if lt < 8:
            img = zoom_burst(img, 0.5 * (1 - lt / 8))
            img = img + 0.4 * (1 - lt / 8)
        img = warp_scale(img, 1.0 + 0.012 * beat_env(f, 270))
        if f >= 380:
            img = zoom_burst(img, 0.6 * ((f - 380) / 10) ** 2)
            img = img + 0.5 * ((f - 380) / 10) ** 3

    # ---------------- 390-480: call to action
    else:
        lt = f - 390
        k = (f - 390) / 30
        e = back(min(1, k), 1.3)
        ry = 3 * np.pi * (1 - ease(min(1, k))) + 0.25 * np.sin(t * 1.4)
        img = shockwave(img, W / 2, 640, 60 + lt * 50, max(0, 1 - lt / 14))
        img = particle_burst(img, W / 2, 640, lt / 24)
        img = logo3d(img, W / 2, 620 + 20 * np.sin(t * 2.0), mix(200, 560, e), 0.12 + 0.06 * np.sin(t), ry, glow=0.45)
        for j, (word, st) in enumerate((("KOSTENLOSES", 400), ("ERSTGESPRÄCH", 405))):
            if f >= st:
                kk = (f - st) / 14
                img = title(img, word, 112, W / 2, 1040 + j * 135 + 8 * np.sin(t * 2 + j), rx=0.12,
                            ry=mix(1.0 * (-1) ** j, 0, back(kk, 1.2)) + 0.04 * np.sin(t + j),
                            dist=mix(2.4, 1.0, back(kk, 1.1)), opacity=min(1, kk * 2), depth=30,
                            top=(1.0, 0.72, 0.40) if j == 1 else (1, 1, 1), bot=(0.92, 0.42, 0.12) if j == 1 else (0.85, 0.85, 0.9),
                            spec_pos=(f - st) / 40)
        if f >= 420:
            kb = back((f - 420) / 12, 1.6)
            pulse = 1 + 0.05 * beat_env(f, 420, FPB * 2)
            img = place(img, BUTTON[0], BUTTON[1], W / 2, 1460 + 10 * np.sin(t * 2.4), kb * pulse, 0.1 + 0.04 * np.sin(t * 1.3),
                        0.1 * np.sin(t * 1.1), shadow=0.6, glow=0.6 + 0.4 * beat_env(f, 420, FPB * 2))
        if f >= 428:
            img = flat_text(img, "@bakimotions", 1610, ease((f - 428) / 10), 50, 4, FONT_BOLD)
        img = img + 0.8 * np.exp(-lt / 2.5)
        if lt < 8:
            img = zoom_burst(img, 0.5 * (1 - lt / 8))
        img = warp_scale(img, 1.0 + 0.012 * beat_env(f, 390))
        img = img * (1 - ease_io((f - 466) / 13)) if f >= 466 else img
    return np.clip(img, 0, 1)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/baki_raw.mp4"
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

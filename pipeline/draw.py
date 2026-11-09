import skia, math, random
import numpy as np

W, H = 1080, 1920
FD = "/usr/share/fonts/opentype/inter/"
TF = {
    "black": skia.Typeface.MakeFromFile(FD + "Inter-Black.otf"),
    "xbold": skia.Typeface.MakeFromFile(FD + "Inter-ExtraBold.otf"),
    "bold": skia.Typeface.MakeFromFile(FD + "Inter-Bold.otf"),
    "semi": skia.Typeface.MakeFromFile(FD + "Inter-SemiBold.otf"),
    "disp": skia.Typeface.MakeFromFile(FD + "InterDisplay-Black.otf"),
    "lilita": skia.Typeface.MakeFromFile("/home/claude/fonts/LilitaOne-Regular.ttf"),
    "bungee": skia.Typeface.MakeFromFile("/home/claude/fonts/Bungee-Regular.ttf"),
}


def C(h, a=255):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


INK = "#1A1A1A"
SKIN = "#DCA880"
HAIR = "#2A1F18"
SHIRT = "#F0904D"
STAIN = "#C96F3A"
PIMPLE = "#D0524E"


def fillp(col, a=255):
    return skia.Paint(AntiAlias=True, Color=C(col, a), Style=skia.Paint.kFill_Style)


def strokep(col, w, a=255, cap=skia.Paint.kRound_Cap):
    return skia.Paint(AntiAlias=True, Color=C(col, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)


def both(c, draw, fill, sw, ink=INK, a=255):
    """draw(paint) called twice: fill then outline"""
    if fill:
        draw(fillp(fill, a))
    if sw:
        draw(strokep(ink, sw, a))


def oval(c, cx, cy, rx, ry, fill, sw=0, ink=INK, a=255):
    r = skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)
    both(c, lambda p: c.drawOval(r, p), fill, sw, ink, a)


def circ(c, cx, cy, r, fill, sw=0, ink=INK, a=255):
    both(c, lambda p: c.drawCircle(cx, cy, r, p), fill, sw, ink, a)


def rrect(c, x, y, w, h, r, fill, sw=0, ink=INK, a=255):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    both(c, lambda p: c.drawRRect(rr, p), fill, sw, ink, a)


def path(pts_cmds):
    p = skia.Path()
    for cmd in pts_cmds:
        getattr(p, cmd[0])(*cmd[1:])
    return p


def drawpath(c, p, fill, sw=0, ink=INK, a=255):
    both(c, lambda pa: c.drawPath(p, pa), fill, sw, ink, a)


def font(name, size):
    f = skia.Font(TF[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text(c, s, x, y, name, size, col=INK, align="c", a=255, stroke=0, stroke_col=INK):
    f = font(name, size)
    w = f.measureText(s)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    if stroke:
        c.drawString(s, x, y, f, strokep(stroke_col, stroke, a))
    c.drawString(s, x, y, f, fillp(col, a))
    return w


def tw(s, name, size):
    return font(name, size).measureText(s)


# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return clamp((t - t0) / d)


def eo(x):  # ease out cubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def back(x, s=1.9):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def elastic(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1


def pop(c, t, t0, cx, cy, d=0.35, kind="back"):
    """scale-in around cx,cy. returns scale (0 => skip)"""
    x = prog(t, t0, d)
    s = back(x) if kind == "back" else elastic(x)
    c.translate(cx, cy)
    c.scale(max(s, 0.001), max(s, 0.001))
    c.translate(-cx, -cy)
    return s


# ---------------- background ----------------
def background(c, t, col, ray=None, rot_speed=6, dots=True, ray_alpha=255):
    c.clear(C(col))
    if ray:
        c.save()
        c.translate(W / 2, H * 0.62)
        c.rotate(t * rot_speed)
        n = 18
        p = fillp(ray, ray_alpha)
        for k in range(n):
            a0 = 2 * math.pi * k / n
            a1 = a0 + math.pi / n
            R = 2400
            pa = skia.Path()
            pa.moveTo(0, 0)
            pa.lineTo(R * math.cos(a0), R * math.sin(a0))
            pa.lineTo(R * math.cos(a1), R * math.sin(a1))
            pa.close()
            c.drawPath(pa, p)
        c.restore()
    if dots:
        p = fillp("#000000", 16)
        off = (t * 12) % 44
        y = -44 + off
        while y < H + 44:
            x = -44 + off
            while x < W + 44:
                c.drawCircle(x, y, 3.2, p)
                x += 44
            y += 44


def iris(c, t, t0, col, d=0.45, cx=W / 2, cy=H / 2, prev=None):
    """circle wipe in of new bg colour (draws prev colour underneath)"""
    x = prog(t, t0, d)
    if x >= 1:
        return False
    if prev:
        c.clear(C(prev))
    r = eio(x) * 1250
    c.save()
    pa = skia.Path()
    pa.addCircle(cx, cy, r)
    c.clipPath(pa, doAntiAlias=True)
    return True


# ---------------- UI bits ----------------
def card(c, x, y, w, h, fill="#FFFFFF", r=34, sh=12, sw=7, a=255):
    rrect(c, x + sh, y + sh, w, h, r, INK, 0, a=a)
    rrect(c, x, y, w, h, r, fill, sw, a=a)


def pill(c, s, cx, cy, size=44, fill=INK, col="#FFFFFF", name="xbold", padx=34, pady=20, a=255):
    w = tw(s, name, size) + padx * 2
    h = size + pady * 2
    rrect(c, cx - w / 2 + 8, cy - h / 2 + 8, w, h, h / 2 if h < 120 else 30, "#000000", 0, a=int(a * 0.25))
    rrect(c, cx - w / 2, cy - h / 2, w, h, 22, fill, 0, a=a)
    text(c, s, cx, cy + size * 0.36, name, size, col, a=a)
    return w, h


def title(c, t, t0, s, cy, size=150, col="#FFFFFF", wob=True, name="lilita"):
    x = prog(t, t0, 0.45)
    if x <= 0:
        return
    sc = 2.2 - 1.2 * back(x, 2.4) if x < 1 else 1.0
    c.save()
    c.translate(W / 2, cy)
    ang = math.sin(t * 2.2) * 2.0 if wob else 0
    c.rotate(ang)
    c.scale(sc, sc)
    a = int(255 * clamp(x * 3))
    text(c, s, 10, 12 + size * 0.35, name, size, INK, a=a, stroke=24)
    text(c, s, 0, size * 0.35, name, size, col, a=a, stroke=22, stroke_col=INK)
    text(c, s, 0, size * 0.35, name, size, col, a=a)
    c.restore()


def heart_path(cx, cy, s):
    p = skia.Path()
    p.moveTo(cx, cy + s * 0.9)
    p.cubicTo(cx - s * 1.35, cy + s * 0.05, cx - s * 0.9, cy - s * 1.05, cx, cy - s * 0.35)
    p.cubicTo(cx + s * 0.9, cy - s * 1.05, cx + s * 1.35, cy + s * 0.05, cx, cy + s * 0.9)
    p.close()
    return p


def heart(c, cx, cy, s, col="#F0507F", sw=6, a=255):
    drawpath(c, heart_path(cx, cy, s), col, sw, a=a)
    if s > 18:
        oval(c, cx - s * 0.45, cy - s * 0.35, s * 0.16, s * 0.11, "#FFFFFF", a=int(a * 0.7))


def xmark(c, cx, cy, r=34):
    circ(c, cx, cy, r, "#E5484D", 6)
    p = strokep("#FFFFFF", 9)
    d = r * 0.42
    c.drawLine(cx - d, cy - d, cx + d, cy + d, p)
    c.drawLine(cx + d, cy - d, cx - d, cy + d, p)


def checkmark(c, cx, cy, r=34):
    circ(c, cx, cy, r, "#2FBF71", 6)
    p = strokep("#FFFFFF", 10)
    c.drawLine(cx - r * 0.45, cy + r * 0.02, cx - r * 0.1, cy + r * 0.35, p)
    c.drawLine(cx - r * 0.1, cy + r * 0.35, cx + r * 0.48, cy - r * 0.35, p)


# ---------------- AHMED ----------------
def ahmed_head(c, st, t):
    """drawn in reference-face coordinates (approx 1170x1150 space), head centre (585,470)"""
    mouth = st.get("mouth", 0.0)
    eyes = st.get("eyes", "derp")
    look = st.get("look", (0, 0))
    mshape = st.get("mshape", "smile")
    blink = st.get("blink", False)
    # ears
    circ(c, 165, 465, 78, SKIN, 13)
    circ(c, 1005, 465, 78, SKIN, 13)
    # face
    oval(c, 585, 470, 425, 398, SKIN, 14)
    # hair
    hp = skia.Path()
    hp.moveTo(178, 345)
    hp.cubicTo(165, 200, 230, 110, 330, 92)
    hp.cubicTo(390, 80, 430, 85, 455, 92)
    hp.cubicTo(470, 40, 540, 15, 600, 40)
    hp.cubicTo(640, 60, 650, 72, 660, 75)
    hp.cubicTo(720, 35, 820, 55, 875, 155)
    hp.cubicTo(960, 175, 1005, 250, 990, 370)
    hp.cubicTo(940, 300, 870, 255, 785, 255)
    hp.cubicTo(740, 255, 700, 262, 685, 262)
    hp.cubicTo(640, 220, 520, 212, 440, 262)
    hp.cubicTo(400, 250, 300, 230, 178, 345)
    hp.close()
    drawpath(c, hp, HAIR, 13)
    # blush
    oval(c, 318, 582, 62, 33, "#E0907E", a=170)
    oval(c, 852, 582, 62, 33, "#E0907E", a=170)
    # eyebrows (unibrow)
    sad = eyes in ("sad", "wide") or st.get("worried", False)
    bp = skia.Path()
    lift = -18 if eyes == "wide" else 0
    if sad:
        bp.moveTo(330, 330 + lift)
        bp.quadTo(440, 305 + lift, 540, 340 + lift)
        bp.quadTo(585, 300 + lift, 630, 340 + lift)
        bp.quadTo(730, 305 + lift, 840, 330 + lift)
    else:
        bp.moveTo(325, 348)
        bp.quadTo(440, 270, 540, 365)
        bp.quadTo(585, 325, 630, 365)
        bp.quadTo(730, 270, 845, 348)
    c.drawPath(bp, strokep(HAIR, 34))
    # eyes
    ex = [(452, 445), (718, 445)]
    if eyes == "heart":
        pulse = 1 + 0.12 * math.sin(t * 14)
        for (x, y) in ex:
            heart(c, x, y + 5, 70 * pulse, "#F0507F", 12)
    else:
        er = 74 if eyes == "wide" else 65
        for k, (x, y) in enumerate(ex):
            circ(c, x, y, er, "#FFFFFF", 12)
            if blink:
                c.drawLine(x - er + 8, y, x + er - 8, y, strokep(INK, 12))
                continue
            if eyes == "derp":
                px, py = (26, 13) if k == 0 else (-30, -10)
            elif eyes == "sad":
                px, py = (0, 26)
            elif eyes == "wide":
                px, py = (0, 0)
            else:
                px, py = (0, 0)
            px += look[0]
            py += look[1]
            pr = 15 if eyes == "wide" else 25
            circ(c, x + px, y + py, pr, INK)
            circ(c, x + px - 7, y + py - 8, 6, "#FFFFFF")
            if eyes == "smug":
                lid = skia.Path()
                lid.addCircle(x, y, er - 4)
                c.save()
                c.clipPath(lid, doAntiAlias=True)
                c.drawRect(skia.Rect.MakeLTRB(x - er, y - er, x + er, y - 4), fillp(SKIN))
                c.restore()
                c.drawLine(x - er + 6, y - 4, x + er - 6, y - 4, strokep(INK, 12))
    # nose
    oval(c, 585, 565, 92, 70, "#CF9068", 12)
    circ(c, 552, 588, 11, INK)
    circ(c, 618, 588, 11, INK)
    # pimples
    for (x, y, r) in [(585, 285, 33), (240, 397, 20), (312, 525, 27), (835, 520, 32), (657, 575, 22), (378, 688, 20), (797, 665, 23)]:
        circ(c, x, y, r, PIMPLE)
        circ(c, x - r * 0.3, y - r * 0.3, r * 0.36, "#FFF1C2")
    # stubble moustache
    sp = skia.Path()
    sp.moveTo(450, 655)
    sp.quadTo(585, 620, 715, 655)
    dash = skia.Paint(AntiAlias=True, Color=C(HAIR), Style=skia.Paint.kStroke_Style, StrokeWidth=13, StrokeCap=skia.Paint.kRound_Cap,
                      PathEffect=skia.DashPathEffect.Make([22, 14], 0))
    c.drawPath(sp, dash)
    # double chin
    cp = skia.Path()
    cp.moveTo(330, 748)
    cp.quadTo(585, 870, 840, 748)
    c.drawPath(cp, strokep(INK, 10))
    # mouth
    jaw = 0
    if mshape == "smile":
        o = mouth
        mp = skia.Path()
        mp.moveTo(402, 682)
        mp.quadTo(585, 715, 770, 682)
        mp.quadTo(585, 745 + o * 110, 402, 682)
        mp.close()
        drawpath(c, mp, "#73302F", 12)
        tongue_y = 735 + o * 70
        if o > 0.35:
            c.save()
            c.clipPath(mp, doAntiAlias=True)
            oval(c, 585, tongue_y, 90, 40, "#D9686A")
            c.restore()
            drawpath(c, mp, None, 12)
        rrect(c, 557, 694, 56, 46, 6, "#FFFFFF", 7)
        jaw = o * 30
    elif mshape == "o":
        o = 0.35 + mouth * 0.65
        oval(c, 585, 720 + o * 10, 48 + 18 * o, 30 + 48 * o, "#73302F", 12)
        rrect(c, 563, 693 - 0 * o, 44, 30, 5, "#FFFFFF", 6)
        jaw = o * 20
    elif mshape == "grimace":
        o = mouth
        h = 62 + o * 30
        rrect(c, 472, 678, 226, h, 26, "#FFFFFF", 12)
        for k in range(1, 5):
            x = 472 + k * 226 / 5
            c.drawLine(x, 682, x, 678 + h - 4, strokep(INK, 6))
        c.drawLine(476, 678 + h / 2, 694, 678 + h / 2, strokep(INK, 6))
        jaw = o * 15
    elif mshape == "sad":
        o = mouth
        mp = skia.Path()
        mp.moveTo(450, 740)
        mp.quadTo(585, 655 - o * 20, 720, 740)
        if o > 0.08:
            mp.quadTo(585, 700 + o * 60, 450, 740)
            mp.close()
            drawpath(c, mp, "#73302F", 12)
        else:
            c.drawPath(mp, strokep(INK, 13))
        jaw = o * 12
    elif mshape == "grin":  # smug closed grin
        o = mouth
        mp = skia.Path()
        mp.moveTo(430, 680)
        mp.quadTo(585, 740, 760, 665)
        mp.quadTo(585, 770 + o * 60, 430, 680)
        mp.close()
        drawpath(c, mp, "#FFFFFF", 12)
        c.drawLine(440, 693, 748, 678, strokep(INK, 6))
        jaw = o * 15
    # goatee
    gp = skia.Path()
    gp.moveTo(500, 762 + jaw)
    gp.quadTo(585, 790 + jaw, 670, 762 + jaw)
    gp.lineTo(630, 850 + jaw)
    gp.quadTo(585, 885 + jaw, 540, 850 + jaw)
    gp.close()
    drawpath(c, gp, HAIR, 10)
    # sweat
    n_sweat = st.get("sweat", 1)
    for k in range(n_sweat):
        sx, sy = [(955, 430), (220, 300), (900, 250), (260, 470)][k % 4]
        dy = ((t * 70 + k * 37) % 60) if n_sweat > 1 else math.sin(t * 3) * 6
        dp = skia.Path()
        s = 1.0
        dp.moveTo(sx, sy - 55 * s + dy)
        dp.cubicTo(sx + 30, sy - 10 + dy, sx + 35, sy + 30 + dy, sx, sy + 38 + dy)
        dp.cubicTo(sx - 35, sy + 30 + dy, sx - 30, sy - 10 + dy, sx, sy - 55 * s + dy)
        dp.close()
        drawpath(c, dp, "#8FD3FF", 7, ink="#3A6E91")


def phone(c, x, y, ang, sc=1.0, buzz=0.0, t=0):
    c.save()
    c.translate(x + (math.sin(t * 90) * 6 * buzz), y)
    c.rotate(ang)
    c.scale(sc, sc)
    rrect(c, -34, -60, 68, 120, 14, "#F27BAE", 7)
    rrect(c, -24, -48, 48, 88, 6, "#FFD1E4", 0)
    c.restore()


def ahmed(c, t, x, y, s, st=None):
    """x,y = feet centre on canvas. s = scale (1.0 ~ 715px tall)"""
    st = st or {}
    bob = st.get("bob", 1.0)
    breathe = math.sin(t * 3.2) * 0.012 * bob
    hop = st.get("hop", 0.0)
    c.save()
    c.translate(x, y - hop)
    c.scale(s * (1 + breathe * 0.6), s * (1 - breathe))
    c.translate(-330, -705)
    # shadow
    c.save()
    c.translate(330, 705 + hop / s)
    shs = 1 - min(hop / 400, 0.4)
    c.scale(shs, shs)
    oval(c, 0, 0, 200, 20, "#000000", a=45)
    c.restore()
    # feet
    oval(c, 262, 683, 58, 24, "#1E1E1E")
    oval(c, 398, 683, 58, 24, "#1E1E1E")
    # left arm (behind)
    la = st.get("larm", 0) + math.sin(t * 3.2 + 1) * 3
    c.save()
    c.translate(140, 395)
    c.rotate(la)
    oval(c, -18, 70, 42, 100, SHIRT, 11)
    circ(c, -28, 165, 36, SKIN, 11)
    if st.get("phone_l"):
        phone(c, -10, 125, -12, 1.0, st.get("buzz", 0), t)
        circ(c, -28, 165, 36, SKIN, 11)
    c.restore()
    # belly
    oval(c, 330, 565, 210, 118, SKIN, 11)
    bb = skia.Path()
    bb.moveTo(316, 650)
    bb.quadTo(330, 660, 344, 650)
    c.drawPath(bb, strokep(INK, 6))
    # shirt
    sp = skia.Path()
    sp.moveTo(122, 602)
    sp.cubicTo(105, 520, 98, 455, 140, 395)
    sp.cubicTo(180, 340, 260, 330, 330, 330)
    sp.cubicTo(400, 330, 480, 340, 520, 395)
    sp.cubicTo(562, 455, 555, 520, 540, 602)
    sp.quadTo(330, 590, 122, 602)
    sp.close()
    drawpath(c, sp, st.get("shirt", SHIRT), 11)
    text(c, "100%", 300, 482, "bungee", 40, INK)
    text(c, "SINGLE", 300, 528, "bungee", 40, INK)
    # stain
    for (dx, dy, r) in [(0, 0, 30), (22, -16, 18), (-20, 14, 16), (18, 22, 17), (-14, -20, 15)]:
        circ(c, 415 + dx, 515 + dy, r, STAIN)
    # right arm
    ra = st.get("rarm", -25)
    wave = st.get("wave", 0)
    ra += math.sin(t * 12) * 14 * wave
    c.save()
    c.translate(515, 400)
    c.rotate(ra)
    oval(c, 20, 75, 44, 105, SHIRT, 11)
    if st.get("phone_r"):
        phone(c, 22, 150, 10, 1.0, st.get("buzz", 0), t)
    circ(c, 26, 178, 37, SKIN, 11)
    c.restore()
    # head
    tilt = st.get("tilt", 0) + math.sin(t * 2.1) * 2 * bob
    c.save()
    c.translate(331, 330)
    c.rotate(tilt)
    c.translate(-331, -330)
    c.translate(331, 232)
    c.scale(0.388, 0.388)
    c.translate(-585, -470)
    ahmed_head(c, st, t)
    c.restore()
    c.restore()


# ---------------- EMRE (the cousin) ----------------
def emre(c, cx, cy, s, t):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    # torso V
    tp = skia.Path()
    tp.moveTo(-230, 420)
    tp.cubicTo(-240, 260, -200, 180, -120, 160)
    tp.lineTo(120, 160)
    tp.cubicTo(200, 180, 240, 260, 230, 420)
    tp.close()
    drawpath(c, tp, "#C98F66", 10)
    # tank top
    kp = skia.Path()
    kp.moveTo(-150, 420)
    kp.lineTo(-130, 230)
    kp.quadTo(-100, 175, -70, 190)
    kp.quadTo(0, 285, 70, 190)
    kp.quadTo(100, 175, 130, 230)
    kp.lineTo(150, 420)
    kp.close()
    drawpath(c, kp, "#FFFFFF", 10)
    # pecs line
    c.drawLine(-60, 300, 60, 300, strokep("#DDDDDD", 6))
    # neck
    rrect(c, -48, 80, 96, 110, 30, "#C98F66", 10)
    # head
    hp = skia.Path()
    hp.moveTo(-105, -40)
    hp.cubicTo(-110, -150, 110, -150, 105, -40)
    hp.cubicTo(105, 60, 50, 125, 0, 128)
    hp.cubicTo(-50, 125, -105, 60, -105, -40)
    hp.close()
    drawpath(c, hp, "#D49C72", 10)
    # slick hair
    sp = skia.Path()
    sp.moveTo(-112, -30)
    sp.cubicTo(-130, -150, -20, -190, 60, -170)
    sp.cubicTo(120, -160, 135, -90, 110, -30)
    sp.cubicTo(90, -95, 20, -110, -40, -95)
    sp.cubicTo(-80, -90, -100, -60, -112, -30)
    sp.close()
    drawpath(c, sp, "#1D1512", 9)
    # sunglasses
    rrect(c, -95, -30, 82, 46, 16, "#111111", 6)
    rrect(c, 13, -30, 82, 46, 16, "#111111", 6)
    c.drawLine(-13, -14, 13, -14, strokep(INK, 7))
    c.drawLine(-80, -22, -45, -22, strokep("#FFFFFF", 6, 160))
    c.drawLine(28, -22, 63, -22, strokep("#FFFFFF", 6, 160))
    # smile
    mp = skia.Path()
    mp.moveTo(-50, 60)
    mp.quadTo(0, 100, 50, 60)
    mp.close()
    drawpath(c, mp, "#FFFFFF", 7)
    # sparkle
    sx = 100 + 10 * math.sin(t * 5)
    star(c, 120, 55, 26 * (0.8 + 0.3 * math.sin(t * 8)), "#FFFFFF")
    c.restore()


def star(c, cx, cy, r, col, sw=0):
    p = skia.Path()
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.28
        a = k * math.pi / 4 - math.pi / 2
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if k == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    drawpath(c, p, col, sw)


# ---------------- LENA avatar ----------------
def lena_avatar(c, cx, cy, r):
    c.save()
    cl = skia.Path()
    cl.addCircle(cx, cy, r)
    c.clipPath(cl, doAntiAlias=True)
    c.drawCircle(cx, cy, r, fillp("#FFB3C7"))
    s = r / 100
    # hair back
    oval(c, cx, cy + 10 * s, 70 * s, 85 * s, "#F2C14E")
    rrect(c, cx - 70 * s, cy, 140 * s, 110 * s, 20 * s, "#F2C14E")
    # shoulders
    oval(c, cx, cy + 120 * s, 75 * s, 45 * s, "#7C5CFF", 5 * s)
    # face
    oval(c, cx, cy - 2 * s, 46 * s, 52 * s, "#F6CDB0", 5 * s)
    # fringe
    fp = skia.Path()
    fp.moveTo(cx - 52 * s, cy - 5 * s)
    fp.cubicTo(cx - 55 * s, cy - 75 * s, cx + 55 * s, cy - 75 * s, cx + 52 * s, cy - 5 * s)
    fp.cubicTo(cx + 20 * s, cy - 35 * s, cx - 20 * s, cy - 40 * s, cx - 52 * s, cy - 5 * s)
    fp.close()
    drawpath(c, fp, "#F2C14E", 4 * s)
    circ(c, cx - 16 * s, cy + 2 * s, 5 * s, INK)
    circ(c, cx + 16 * s, cy + 2 * s, 5 * s, INK)
    oval(c, cx - 28 * s, cy + 18 * s, 9 * s, 5 * s, "#F49AA6")
    oval(c, cx + 28 * s, cy + 18 * s, 9 * s, 5 * s, "#F49AA6")
    mp = skia.Path()
    mp.moveTo(cx - 13 * s, cy + 22 * s)
    mp.quadTo(cx, cy + 34 * s, cx + 13 * s, cy + 22 * s)
    c.drawPath(mp, strokep(INK, 4 * s))
    c.restore()
    circ(c, cx, cy, r, None, 7)


def emre_avatar(c, cx, cy, r, t):
    c.save()
    cl = skia.Path()
    cl.addCircle(cx, cy, r)
    c.clipPath(cl, doAntiAlias=True)
    c.drawCircle(cx, cy, r, fillp("#7FD1FF"))
    emre(c, cx, cy + r * 0.25, r / 190, t)
    c.restore()
    circ(c, cx, cy, r, None, 7)


# ---------------- chat phone ----------------
def chat_phone(c, x, y, w, h, msgs, typing_text=None, dots=False, t=0, header="Lena, 24"):
    card(c, x, y, w, h, "#FFFFFF", 56, 16, 9)
    rrect(c, x + 22, y + 22, w - 44, h - 44, 38, "#F4F1EC", 0)
    # header
    rrect(c, x + 22, y + 22, w - 44, 130, 38, "#FFFFFF", 0)
    c.drawLine(x + 22, y + 152, x + w - 22, y + 152, strokep("#E5E0DA", 4))
    lena_avatar(c, x + 92, y + 87, 42)
    text(c, header, x + 150, y + 85, "xbold", 40, INK, "l")
    circ(c, x + 158, y + 112, 7, "#2FBF71")
    text(c, "online", x + 172, y + 120, "semi", 26, "#2FBF71", "l")
    # messages (auto-scroll so the newest stays above the input field)
    iy0 = y + h - 140
    total = 0
    for m in msgs:
        a_ = eo(prog(t, m[2], 0.3))
        if a_ <= 0:
            continue
        ls_ = wrap(m[1], "bold", 36, w - 220)
        total += (36 * 1.3 * len(ls_) + 44 + 24) * a_
    if dots:
        total += 100
    yy = min(y + 190, iy0 - 20 - total)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x + 22, y + 156, x + w - 22, iy0 - 6))
    for m in msgs:
        side, s, appear = m[0], m[1], m[2]
        a = prog(t, appear, 0.25)
        if a <= 0:
            continue
        lines = wrap(s, "bold", 36, w - 220)
        bh = 36 * 1.3 * len(lines) + 44
        bw = max(tw(L, "bold", 36) for L in lines) + 56
        bx = x + 52 if side == "l" else x + w - 52 - bw
        c.save()
        sc = back(a)
        ox = bx if side == "l" else bx + bw
        c.translate(ox, yy + bh)
        c.scale(sc, sc)
        c.translate(-ox, -(yy + bh))
        fill = "#FFFFFF" if side == "l" else "#3B82F6"
        col = INK if side == "l" else "#FFFFFF"
        rrect(c, bx, yy, bw, bh, 30, fill, 5 if side == "l" else 0)
        for k, L in enumerate(lines):
            text(c, L, bx + 28, yy + 22 + 36 + k * 36 * 1.3 - 6, "bold", 36, col, "l")
        c.restore()
        yy += bh + 24
    if dots:
        bx = x + 52
        rrect(c, bx, yy, 150, 76, 30, "#FFFFFF", 5)
        for k in range(3):
            dy = math.sin(t * 10 - k * 0.9) * 8
            circ(c, bx + 42 + k * 33, yy + 38 + dy, 10, "#9A9A9A")
    c.restore()
    # input field
    iy = y + h - 140
    rrect(c, x + 44, iy, w - 88, 92, 46, "#FFFFFF", 5)
    if typing_text is not None:
        s = typing_text
        f = font("semi", 34)
        maxw = w - 220
        while f.measureText(s) > maxw and len(s) > 1:
            s = s[1:]
        text(c, s, x + 80, iy + 58, "semi", 34, INK, "l")
        if int(t * 2.5) % 2 == 0:
            cx = x + 84 + f.measureText(s)
            c.drawLine(cx, iy + 24, cx, iy + 68, strokep("#3B82F6", 4))
    else:
        text(c, "Nachricht…", x + 80, iy + 58, "semi", 34, "#A0A0A0", "l")
    circ(c, x + w - 98, iy + 46, 34, "#3B82F6")
    p = skia.Path()
    p.moveTo(x + w - 112, iy + 30)
    p.lineTo(x + w - 80, iy + 46)
    p.lineTo(x + w - 112, iy + 62)
    p.close()
    c.drawPath(p, fillp("#FFFFFF"))


def wrap(s, name, size, maxw):
    words = s.split(" ")
    lines, cur = [], ""
    for wd in words:
        tst = (cur + " " + wd).strip()
        if tw(tst, name, size) > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = tst
    if cur:
        lines.append(cur)
    return lines


# ---------------- caption bubble ----------------
def caption(c, t, who, chunk_words, cy, tail_x=None, appear=0.0):
    """chunk_words: list of (word, start). highlight words already spoken"""
    size = 58
    s = " ".join(w for w, _ in chunk_words)
    lines = wrap(s, "black", size, 860)
    lh = size * 1.18
    bw = max(tw(L, "black", size) for L in lines) + 90
    bh = lh * len(lines) + 92
    bx = W / 2 - bw / 2
    by = cy - bh / 2
    a = prog(t, appear, 0.18)
    c.save()
    sc = 0.7 + 0.3 * back(a)
    c.translate(W / 2, cy)
    c.scale(sc, sc)
    c.translate(-W / 2, -cy)
    is_l = who == "L"
    fill = "#FFFFFF" if not is_l else "#FFE1EC"
    rrect(c, bx + 12, by + 12, bw, bh, 34, INK)
    rrect(c, bx, by, bw, bh, 34, fill, 8)
    if tail_x:
        tp = skia.Path()
        tp.moveTo(tail_x - 30, by + bh - 4)
        tp.lineTo(tail_x + 10, by + bh + 50)
        tp.lineTo(tail_x + 32, by + bh - 4)
        drawpath(c, tp, fill, 0)
        c.drawLine(tail_x - 30, by + bh - 1, tail_x + 10, by + bh + 50, strokep(INK, 8))
        c.drawLine(tail_x + 10, by + bh + 50, tail_x + 32, by + bh - 1, strokep(INK, 8))
    lab = "AHMED" if not is_l else "LENA"
    text(c, lab, W / 2, by + 40, "black", 26, "#E0245E")
    # words with highlight
    idx = 0
    for k, L in enumerate(lines):
        ws = L.split(" ")
        lw = tw(L, "black", size)
        xx = W / 2 - lw / 2
        yy = by + 58 + size * 0.85 + k * lh
        for wd in ws:
            start = chunk_words[idx][1] if idx < len(chunk_words) else 1e9
            spoken = t >= start
            col = INK if spoken else "#B9B2AA"
            if spoken and t - start < 0.18 and not is_l:
                col = "#E0245E"
            ww = text(c, wd, xx, yy, "black", size, col, "l")
            xx += ww + tw(" ", "black", size)
            idx += 1
    c.restore()

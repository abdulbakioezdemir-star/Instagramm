"""Valmora – Tag 1: Gründung. Rendert Audio + Video (1080x1920, 30 fps)."""
import numpy as np, json, subprocess, math, os
from scipy.signal import butter, sosfilt, fftconvolve
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 48000
rng = np.random.default_rng(3)
exec(open("synth_body.py").read())
FB = "/home/claude/instagramm/pipeline/fonts/Bungee-Regular.ttf"
FL = "/home/claude/instagramm/pipeline/fonts/LilitaOne-Regular.ttf"

# ---------------- timeline ----------------
def dec(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)

gaps = {"l1": 0.25, "l2": 0.5, "l3": 0.7, "l4": 0.6, "l5": 0.7, "l6": 0.45, "l7": 0.45, "l8": 0.45, "l9": 0.8}
t = 0.0
L = {}
for i in range(1, 10):
    k = f"l{i}"
    a = dec(f"{k}.mp3")
    t += gaps[k]
    words = json.load(open(f"{k}.mp3.json"))
    L[k] = dict(t0=t, t1=t + len(a) / SR, audio=a, words=[(t + o, d, w) for o, d, w in words])
    t = L[k]["t1"]
TOTAL = t + 1.8
N = int(TOTAL * SR) + SR
print("total", TOTAL)

S = {  # scene windows
    "hook": (0, L["l2"]["t0"] - 0.2),
    "land": (L["l2"]["t0"] - 0.2, L["l3"]["t0"] - 0.3),
    "name": (L["l3"]["t0"] - 0.3, L["l5"]["t0"] - 0.35),
    "rules": (L["l5"]["t0"] - 0.35, L["l9"]["t0"] - 0.4),
    "tent": (L["l9"]["t0"] - 0.4, TOTAL),
}

# ---------------- audio ----------------
voice = np.zeros(N)
for k, v in L.items():
    add(voice, v["t0"], v["audio"].astype(np.float64), 1.0)
sfx = np.zeros(N)
add(sfx, 0.0, braam(36, 2.2), 0.55)
add(sfx, S["land"][0], whoosh(0.6), 0.5)
add(sfx, L["l3"]["t0"] - 0.6, riser(0.6), 0.4)
add(sfx, L["l3"]["t0"] + 0.9, taiko(1.0), 0.8)
add(sfx, L["l3"]["t0"] + 0.9, cymbal_swell(1.4), 0.25)
add(sfx, L["l4"]["t1"] - 0.3, pop(), 0.5)
for k in ("l5", "l6", "l7", "l8"):
    add(sfx, L[k]["t0"] - 0.1, whoosh(0.35), 0.4)
for j in range(5):
    add(sfx, L["l6"]["t0"] + 0.6 + j * 0.12, coin(), 0.35)
add(sfx, L["l7"]["t0"] + 0.4, pop(500, 1200), 0.5)
add(sfx, L["l9"]["t0"] - 0.3, whoosh(0.6), 0.35)
for j in range(4):
    add(sfx, L["l9"]["t0"] + 0.5 + j * 1.1, bell(mtof(88 + (j % 2) * 3), 1.0, 0.12), 0.6)

mus = np.zeros(N)
exec(open("/home/claude/nwork/arr.py").read()) if os.path.exists("/home/claude/nwork/arr.py") else None
bar = 2.0
Am, F, C, G = (57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)
t0 = 0.0
k = 0
while t0 < TOTAL:
    ch = [Am, F, C, G][k % 4]
    for m in ch:
        add(mus, t0, strings(mtof(m), bar, att=0.6, rel=0.9, bright=1800), 0.18)
    add(mus, t0, strings(mtof(ch[0] - 24), bar, att=0.4, rel=0.9, bright=600), 0.25)
    if t0 >= S["rules"][0] - 0.5 and t0 < S["tent"][0]:
        for j in range(4):
            add(mus, t0 + j * bar / 4, taiko(0.5 + 0.2 * (j == 0)), 0.18)
    if t0 >= S["name"][0] - 1:
        notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]
        for j in range(8):
            add(mus, t0 + j * bar / 8, piano(mtof(notes[[0, 1, 2, 3, 2, 1, 2, 1][j]]), 1.4, 0.45), 0.10)
    t0 += bar
    k += 1
fade = np.ones(N)
e = int(TOTAL * SR)
fade[e - SR:e] = np.linspace(1, 0, SR)
fade[e:] = 0
mus *= fade

def wav(name, x, norm=None):
    if norm:
        x = x / (np.abs(x).max() + 1e-9) * norm
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", name],
                   input=x.tobytes(), check=True)
wav("voice.wav", voice)
wav("sfx.wav", sfx, 0.8)
wav("music.wav", mus, 0.7)
subprocess.run(["bash", "-c", """ffmpeg -nostdin -v error -y -i voice.wav -i sfx.wav -i music.wav -filter_complex "
[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1.5,asplit=2[v][key];
[2:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=350[md];
[1:a]volume=0.75[s];[v][s][md]amix=inputs=3:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=10[out]" -map "[out]" -ar 48000 -ac 2 mix.wav"""], check=True)

# ---------------- visuals ----------------
def font(p, s): return ImageFont.truetype(p, s)
fB = {s: font(FB, s) for s in (44, 56, 64, 80, 110, 150, 170)}
fL = {s: font(FL, s) for s in (52, 64, 76, 92)}
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
def clamp(x): return max(0.0, min(1.0, x))

def sky(d, top, bot, y0=0, y1=H):
    for y in range(y0, y1, 4):
        tt = (y - y0) / (y1 - y0)
        d.rectangle([0, y, W, y + 4], fill=tuple(int(top[i] + (bot[i] - top[i]) * tt) for i in range(3)))

def landscape(img, tt, night=0.0, sun_y=760, zoom=1.0):
    d = ImageDraw.Draw(img)
    day_t, day_b = (255, 178, 102), (230, 120, 110)
    nt_t, nt_b = (10, 18, 40), (34, 40, 80)
    mix = lambda a, b: tuple(int(a[i] + (b[i] - a[i]) * night) for i in range(3))
    sky(d, mix(day_t, nt_t), mix(day_b, nt_b), 0, 1250)
    if night > 0.3:
        r2 = np.random.default_rng(5)
        for _ in range(90):
            x, y = r2.uniform(0, W), r2.uniform(0, 1000)
            b = int(200 * night * (0.6 + 0.4 * math.sin(tt * 3 + x)))
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(b, b, min(255, b + 30)))
        d.ellipse([760, 220, 900, 360], fill=(240, 240, 220))
        d.ellipse([730, 205, 870, 345], fill=mix(day_t, nt_t))
    else:
        d.ellipse([W / 2 - 150, sun_y - 150, W / 2 + 150, sun_y + 150], fill=(255, 220, 110))
    cx = W / 2
    def P(pts): return [(cx + (x - cx) * zoom, 1250 + (y - 1250) * zoom) for x, y in pts]
    mcol = mix((44, 74, 88), (20, 30, 50))
    d.polygon(P([(-200, 1250), (300, 560), (560, 1000), (780, 640), (1300, 1250)]), fill=mcol)
    d.polygon(P([(300, 560), (240, 670), (295, 645), (350, 685), (390, 640)]), fill=mix((245, 248, 252), (120, 130, 160)))
    d.polygon(P([(780, 640), (725, 735), (780, 712), (835, 745), (860, 712)]), fill=mix((245, 248, 252), (120, 130, 160)))
    d.polygon(P([(-200, 1250), (120, 950), (380, 1250)]), fill=mix((60, 104, 84), (24, 40, 46)))
    sea = mix((18, 96, 160), (12, 34, 70))
    d.rectangle([0, 1230, W, H], fill=sea)
    for i, y in enumerate(range(1250, H, 70)):
        off = (tt * 60 * (1 if i % 2 else -1)) % 160
        for x in range(-160, W + 160, 160):
            d.arc([x + off, y, x + off + 160, y + 60], 200, 340, fill=mix((150, 210, 240), (60, 90, 140)), width=10)
    # beach
    d.ellipse([-200, 1200, 700, 1360], fill=mix((236, 206, 150), (70, 66, 70)))
    return d

def flag(d, x, y, s, wave_t):
    d.rectangle([x, y, x + 12 * s, y + 420 * s], fill=(70, 50, 30))
    fw, fh = 300 * s, 200 * s
    pts_top, pts_bot = [], []
    for i in range(21):
        u = i / 20
        dy = math.sin(wave_t * 5 + u * 6) * 14 * s * u
        pts_top.append((x + 12 * s + u * fw, y + dy))
        pts_bot.append((x + 12 * s + u * fw, y + fh + dy))
    d.polygon(pts_top + pts_bot[::-1], fill=(18, 96, 160))
    # orange top half + mountain
    mid = [(px, py + fh * 0.5) for px, py in pts_top]
    d.polygon(pts_top + mid[::-1], fill=(255, 196, 110))
    m0 = pts_top[2]; m1 = pts_top[8]; m2 = pts_top[13]; m3 = pts_top[20]
    d.polygon([(m0[0], m0[1] + fh * 0.65), (m1[0], m1[1] + fh * 0.15), (m2[0] - 10 * s, m2[1] + fh * 0.5),
               (m2[0] + 20 * s, m2[1] + fh * 0.25), (m3[0], m3[1] + fh * 0.65)], fill=(47, 79, 92))

def outlined(d, xy, text, f, fill=(255, 255, 255), stroke=(0, 0, 0), sw=8, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def hud(d, tt, kasse, einw, alpha=1.0):
    if alpha <= 0: return
    y = 120 - (1 - ease(alpha)) * 200
    d.rounded_rectangle([60, y, W - 60, y + 120], radius=34, fill=(12, 30, 52))
    d.rounded_rectangle([60, y, W - 60, y + 120], radius=34, outline=(240, 190, 80), width=5)
    d.text((110, y + 60), "TAG 1", font=fB[56], fill=(240, 190, 80), anchor="lm")
    d.text((W / 2 + 10, y + 60), f"{kasse:,} €".replace(",", "."), font=fB[56], fill=(255, 255, 255), anchor="mm")
    d.text((W - 110, y + 60), f"{einw} EW", font=fB[56], fill=(140, 220, 160), anchor="rm")

def subs(d, tt):
    for k, v in L.items():
        if v["t0"] - 0.05 <= tt <= v["t1"] + 0.15:
            ws = v["words"]
            # chunk into groups of 3 words
            groups = [ws[i:i + 3] for i in range(0, len(ws), 3)]
            for g in groups:
                gs, ge = g[0][0], g[-1][0] + g[-1][1] + 0.12
                if gs - 0.05 <= tt <= ge or (g is groups[-1] and tt <= v["t1"] + 0.15 and tt >= gs):
                    txt = " ".join(w[2] for w in g).upper()
                    cur = max([i for i, w in enumerate(g) if w[0] <= tt] or [0])
                    words = [w[2].upper() for w in g]
                    f = fB[80]
                    widths = [d.textlength(w, font=f) for w in words]
                    tot = sum(widths) + 28 * (len(words) - 1)
                    while tot > W - 120 and f.size > 56:
                        f = fB[64]; widths = [d.textlength(w, font=f) for w in words]; tot = sum(widths) + 22 * (len(words) - 1)
                    x = (W - tot) / 2
                    for i, w in enumerate(words):
                        col = (255, 214, 90) if i == cur else (255, 255, 255)
                        d.text((x, 1500), w, font=f, fill=col, stroke_width=9, stroke_fill=(0, 0, 0), anchor="lm")
                        x += widths[i] + (28 if f.size == 80 else 22)
                    return

LOGO = Image.open("logo_valmora.jpg").convert("RGB")
lm = Image.new("L", LOGO.size, 0)
ImageDraw.Draw(lm).ellipse([LOGO.width * 0.1 - 20, LOGO.height * 0.1 - 20, LOGO.width * 0.9 + 20, LOGO.height * 0.9 + 20], fill=255)

def frame(tt):
    img = Image.new("RGB", (W, H))
    if tt < S["hook"][1]:
        p = tt / S["hook"][1]
        d = ImageDraw.Draw(img)
        landscape(img, tt, night=0.85 - 0.5 * p, sun_y=1300 - 300 * p, zoom=1.0 + 0.08 * p)
        ov = Image.new("RGB", (W, H), (0, 0, 0))
        img = Image.blend(img, ov, 0.55 * (1 - p))
        d = ImageDraw.Draw(img)
        s = ease(tt / 0.4)
        outlined(d, (W / 2, 640), "ICH GRÜNDE", fB[110] if s > 0.5 else fB[80], sw=10)
        outlined(d, (W / 2, 790), "MEIN EIGENES", fB[110], sw=10)
        outlined(d, (W / 2, 950), "LAND", fB[170], fill=(255, 214, 90), sw=12)
    elif tt < S["land"][1]:
        p = (tt - S["land"][0]) / (S["land"][1] - S["land"][0])
        landscape(img, tt, night=0.35 * (1 - p), sun_y=1000 - 260 * ease(p), zoom=1.08 - 0.08 * p)
        d = ImageDraw.Draw(img)
        # tiny explorer on beach
        x = 180 + 260 * p
        d.ellipse([x - 22, 1150, x + 22, 1194], fill=(250, 220, 190))
        d.rounded_rectangle([x - 26, 1190, x + 26, 1260], radius=12, fill=(200, 60, 60))
    elif tt < S["name"][1]:
        p = (tt - S["name"][0]) / (S["name"][1] - S["name"][0])
        landscape(img, tt, sun_y=740)
        d = ImageDraw.Draw(img)
        rise = ease((tt - S["name"][0]) / 1.3)
        flag(d, 330, 1180 - 400 * rise, 1.2, tt)
        if tt > L["l3"]["t0"] + 0.8:
            q = ease((tt - L["l3"]["t0"] - 0.8) / 0.35)
            sz = int(480 * (0.6 + 0.4 * q))
            lg = LOGO.resize((sz, sz)); m = lm.resize((sz, sz))
            img.paste(lg, (int(W / 2 - sz / 2), int(510 - sz / 2)), m)
            d = ImageDraw.Draw(img)
        if tt > L["l4"]["t0"]:
            q = ease((tt - L["l4"]["t0"]) / 0.3)
            d.rounded_rectangle([W / 2 - 300, 1000, W / 2 + 300, 1000 + 130 * q], radius=30, fill=(12, 30, 52))
            if q > 0.8:
                d.text((W / 2, 1065), "EINWOHNER: 1", font=fB[64], fill=(140, 220, 160), anchor="mm")
        hud(d, tt, 1000, 1, clamp((tt - L["l4"]["t0"]) / 0.4))
    elif tt < S["rules"][1]:
        img.paste((12, 30, 52), [0, 0, W, H])
        d = ImageDraw.Draw(img)
        for y in range(0, H, 6):
            g = int(18 + 14 * math.sin(y / 140 + tt))
            d.rectangle([0, y, W, y + 6], fill=(12, g + 12, 52 + g))
        hud(d, tt, 1000, 1)
        outlined(d, (W / 2, 380), "DIE REGELN", fB[110], fill=(240, 190, 80), sw=10)
        cards = [("l5", "START", "1.000 €", (240, 190, 80)), ("l6", "1 LIKE", "= 1 €", (255, 120, 140)),
                 ("l7", "1 FOLLOWER", "= 1 EINWOHNER", (140, 220, 160)), ("l8", "TOP-KOMMENTAR", "= NÄCHSTER BAU", (130, 190, 255))]
        for i, (k, a, b, col) in enumerate(cards):
            st = L[k]["t0"] - 0.1
            if tt < st: continue
            q = ease((tt - st) / 0.35)
            y = 540 + i * 200
            x0 = 80 + (1 - q) * -900
            d.rounded_rectangle([x0, y, x0 + W - 160, y + 170], radius=34, fill=(255, 255, 255))
            d.rounded_rectangle([x0, y, x0 + 30, y + 170], radius=14, fill=col)
            d.text((x0 + 70, y + 55), a, font=fB[56], fill=(12, 30, 52), anchor="lm")
            d.text((x0 + W - 200, y + 120), b, font=fL[64], fill=col if col != (240, 190, 80) else (200, 140, 30), anchor="rm")
    else:
        p = (tt - S["tent"][0]) / (S["tent"][1] - S["tent"][0])
        landscape(img, tt, night=min(1, 0.4 + p * 1.5))
        d = ImageDraw.Draw(img)
        # tent + campfire
        d.polygon([(380, 1215), (520, 1040), (660, 1215)], fill=(220, 120, 50))
        d.polygon([(500, 1215), (520, 1110), (540, 1215)], fill=(60, 30, 20))
        fl_ = 1 + 0.15 * math.sin(tt * 18)
        d.ellipse([720, 1170 - 40 * fl_, 780, 1215], fill=(255, 170, 60))
        d.ellipse([735, 1185 - 20 * fl_, 765, 1215], fill=(255, 235, 140))
        flag(d, 250, 1000, 0.6, tt)
        hud(d, tt, 1000, 1)
        if tt > L["l9"]["t0"] + 2.6:
            q = ease((tt - L["l9"]["t0"] - 2.6) / 0.4)
            s = 0.8 + 0.2 * q + 0.03 * math.sin(tt * 6)
            d.rounded_rectangle([90, 470, W - 90, 800], radius=40, fill=(255, 255, 255))
            outlined(d, (W / 2, 570), "WAS BAUEN WIR", fB[80], fill=(12, 30, 52), stroke=(255, 255, 255), sw=0)
            outlined(d, (W / 2, 690), "ZUERST?", fB[110], fill=(220, 90, 60), stroke=(255, 255, 255), sw=0)
            d.text((W / 2, 870), "↓ TOP-KOMMENTAR ENTSCHEIDET ↓", font=fL[52], fill=(255, 255, 255), anchor="mm",
                   stroke_width=6, stroke_fill=(0, 0, 0))
    d = ImageDraw.Draw(img)
    subs(d, tt)
    return img

nf = int(TOTAL * FPS)
proc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-i", "mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", "valmora_tag01.mp4"], stdin=subprocess.PIPE)
import sys
for i in range(nf):
    proc.stdin.write(frame(i / FPS).tobytes())
    if i % 150 == 0: print(i, nf, file=sys.stderr, flush=True)
proc.stdin.close(); proc.wait()
print("done")

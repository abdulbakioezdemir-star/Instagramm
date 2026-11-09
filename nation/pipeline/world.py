"""Große Valmora-Welt: Panorama (seitlich) und Karte (von oben)."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PW, PH = 3600, 1920
HZ = 1180  # Horizont / Meereshöhe im Panorama
FB = "/home/claude/instagramm/pipeline/fonts/Bungee-Regular.ttf"
FL = "/home/claude/instagramm/pipeline/fonts/LilitaOne-Regular.ttf"
r = np.random.default_rng(11)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def ridge(x0, x1, base, peaks, step=12, seed=0):
    rr = np.random.default_rng(seed)
    pts = []
    for x in range(x0, x1 + step, step):
        y = base
        for (px, ph, pw) in peaks:
            y = min(y, base - ph * math.exp(-((x - px) / pw) ** 2))
        y += rr.uniform(-6, 6)
        pts.append((x, y))
    return pts

def tree(d, x, y, s, col):
    d.polygon([(x, y - 70 * s), (x - 26 * s, y), (x + 26 * s, y)], fill=col)
    d.polygon([(x, y - 100 * s), (x - 20 * s, y - 40 * s), (x + 20 * s, y - 40 * s)], fill=col)
    d.rectangle([x - 4 * s, y, x + 4 * s, y + 12 * s], fill=(70, 50, 35))

def palm(d, x, y, s):
    d.line([(x, y), (x + 12 * s, y - 120 * s)], fill=(110, 80, 50), width=int(10 * s))
    for a in (-2.6, -2.0, -1.2, -0.5, 0.2):
        d.line([(x + 12 * s, y - 120 * s), (x + 12 * s + math.cos(a) * 70 * s, y - 120 * s + math.sin(a) * 40 * s + 25 * s)],
               fill=(50, 140, 70), width=int(12 * s))

def panorama():
    img = Image.new("RGB", (PW, PH))
    d = ImageDraw.Draw(img)
    top, bot = (110, 170, 230), (255, 196, 150)
    for y in range(0, PH, 3):
        d.rectangle([0, y, PW, y + 3], fill=lerp(top, bot, min(1, y / HZ)))
    d.ellipse([2500, 560, 2760, 820], fill=(255, 232, 160))
    # Wolken
    for cx, cy, s in [(400, 260, 1.2), (1300, 180, 1.0), (2100, 300, 1.4), (3100, 220, 1.1)]:
        for k in range(5):
            d.ellipse([cx + k * 70 * s - 90 * s, cy - 40 * s - (k % 2) * 30 * s, cx + k * 70 * s + 60 * s, cy + 40 * s],
                      fill=(255, 250, 245))
    # ferne Bergkette
    far = ridge(-50, 2300, 1050, [(300, 560, 260), (800, 690, 240), (1300, 600, 260), (1800, 480, 300), (2200, 250, 200)], seed=1)
    d.polygon(far + [(2300, HZ), (-50, HZ)], fill=(150, 165, 200))
    for (px, ph, pw) in [(800, 690, 240), (1300, 600, 260), (300, 560, 260)]:
        py = 1050 - ph
        d.polygon([(px, py), (px - pw * 0.45, py + ph * 0.25), (px - pw * 0.15, py + ph * 0.2), (px, py + ph * 0.28),
                   (px + pw * 0.2, py + ph * 0.2), (px + pw * 0.45, py + ph * 0.25)], fill=(245, 248, 255))
    # mittlere Kette mit Schnee
    mid = ridge(-50, 2000, 1150, [(150, 560, 220), (650, 520, 200), (1150, 600, 230), (1650, 360, 240)], seed=2)
    d.polygon(mid + [(2000, HZ + 40), (-50, HZ + 40)], fill=(70, 95, 110))
    for (px, ph, pw) in [(150, 560, 220), (650, 520, 200), (1150, 600, 230)]:
        py = 1150 - ph
        d.polygon([(px, py), (px - pw * 0.4, py + ph * 0.22), (px - pw * 0.1, py + ph * 0.17), (px + pw * 0.12, py + ph * 0.25),
                   (px + pw * 0.4, py + ph * 0.2)], fill=(250, 252, 255))
    # Klippe + Wasserfall
    d.polygon([(1450, 780), (1620, 760), (1660, 1250), (1420, 1250)], fill=(95, 105, 110))
    for k in range(8):
        x = 1530 + k * 8
        d.line([(x, 790), (x + 4, 1210)], fill=(200, 235, 255) if k % 2 else (150, 210, 245), width=10)
    d.ellipse([1460, 1170, 1660, 1260], fill=(235, 248, 255))
    # grüne Hügel / Tal
    hills = ridge(-50, 2700, 1330, [(200, 260, 380), (900, 200, 420), (1950, 140, 380), (2450, 60, 250)], seed=3)
    d.polygon(hills + [(2700, PH), (-50, PH)], fill=(84, 150, 84))
    meadow = ridge(-50, 2900, 1500, [(500, 120, 500), (1500, 90, 600), (2400, 40, 300)], seed=4)
    d.polygon(meadow + [(2900, PH), (-50, PH)], fill=(110, 178, 92))
    # Wälder
    for _ in range(420):
        x = r.uniform(-20, 2350)
        yb = min(p[1] for p in hills if abs(p[0] - x) < 14) if x < 2700 else 1400
        y = r.uniform(yb + 20, yb + 260)
        s = r.uniform(0.6, 1.25) * (0.7 + (y - 1100) / 1400)
        tree(d, x, y, s, lerp((30, 90, 50), (50, 120, 60), r.uniform(0, 1)))
    # Meer + Strand (rechts)
    sea_poly = [(2550, HZ), (PW, HZ), (PW, PH), (2850, PH)]
    d.polygon(sea_poly, fill=(30, 120, 180))
    for i, y in enumerate(range(HZ + 20, PH, 46)):
        for x in range(2600 + (i % 2) * 40, PW, 110):
            if x > 2550 + (y - HZ) * 0.4:
                d.arc([x, y, x + 90, y + 30], 200, 340, fill=(170, 220, 245), width=6)
    d.polygon([(2250, HZ + 70), (2560, HZ), (2700, HZ), (3150, PH), (2150, PH)], fill=(238, 214, 160))
    # Fluss vom Wasserfall zum Meer
    pts = []
    for i in range(80):
        u = i / 79
        x = 1560 + u * 1650
        y = 1255 + u * 420 + math.sin(u * 9) * 60
        pts.append((x, y))
    for w, col in ((70, (60, 140, 200)), (46, (90, 175, 230))):
        for i in range(len(pts) - 1):
            ww = w * (0.6 + 0.8 * i / len(pts))
            d.line([pts[i], pts[i + 1]], fill=col, width=int(ww))
    # Insel
    d.ellipse([3150, HZ + 40, 3450, HZ + 110], fill=(238, 214, 160))
    d.polygon([(3200, HZ + 70), (3290, HZ - 30), (3390, HZ + 70)], fill=(84, 150, 84))
    palm(d, 3330, HZ + 70, 0.8)
    for x, y in [(2700, 1400), (2780, 1650)]:
        palm(d, x, y, 1.1)
    return img

def karte(size=1000):
    S = size
    img = Image.new("RGB", (S, S), (30, 120, 180))
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, S, 40)):
        for x in range((i % 2) * 30, S, 90):
            d.arc([x, y, x + 60, y + 20], 200, 340, fill=(60, 150, 205), width=4)
    coast = []
    for k in range(48):
        a = k / 48 * 2 * math.pi
        rad = 360 + 50 * math.sin(a * 3) + 30 * math.sin(a * 7 + 1) + r.uniform(-10, 10)
        if 5.2 < a < 5.9: rad -= 120  # Bucht
        coast.append((S * 0.45 + math.cos(a) * rad, S * 0.5 + math.sin(a) * rad * 0.95))
    sand = [(S * 0.45 + (x - S * 0.45) * 1.04, S * 0.5 + (y - S * 0.5) * 1.04) for x, y in coast]
    d.polygon(sand, fill=(238, 214, 160))
    d.polygon(coast, fill=(110, 178, 92))
    # Berge oben links
    for _ in range(26):
        x, y = r.uniform(S * 0.15, S * 0.55), r.uniform(S * 0.18, S * 0.42)
        s = r.uniform(26, 48)
        d.polygon([(x, y - s), (x - s * 0.9, y + s * 0.5), (x + s * 0.9, y + s * 0.5)], fill=(90, 100, 110))
        d.polygon([(x, y - s), (x - s * 0.35, y - s * 0.4), (x + s * 0.35, y - s * 0.4)], fill=(250, 252, 255))
    # Wald
    msk = Image.new("L", (S, S), 0); ImageDraw.Draw(msk).polygon([(S*0.45+(x-S*0.45)*0.92, S*0.5+(y-S*0.5)*0.92) for x, y in coast], fill=255)
    for _ in range(220):
        x, y = r.uniform(S * 0.12, S * 0.7), r.uniform(S * 0.45, S * 0.85)
        if not msk.getpixel((int(x), int(y))): continue
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(40, 105, 55))
    # Fluss
    fp = [(S * 0.4 + math.sin(u * 7) * 40 + u * S * 0.38, S * 0.38 + u * S * 0.35) for u in np.linspace(0, 1, 40)]
    d.line(fp, fill=(60, 150, 215), width=14, joint="curve")
    # Insel
    d.ellipse([S * 0.86, S * 0.72, S * 0.95, S * 0.79], fill=(238, 214, 160))
    d.ellipse([S * 0.875, S * 0.73, S * 0.935, S * 0.775], fill=(110, 178, 92))
    # Grenze gestrichelt
    bd = [(S * 0.45 + (x - S * 0.45) * 1.12, S * 0.5 + (y - S * 0.5) * 1.12) for x, y in coast] + [None]
    for i in range(len(coast)):
        a, b = bd[i], bd[(i + 1) % len(coast)]
        if i % 2 == 0:
            d.line([a, b], fill=(235, 70, 70), width=8)
    f = ImageFont.truetype(FL, 34)
    for txt, x, y in [("NORDGEBIRGE", 0.33, 0.13), ("GROSSER WALD", 0.36, 0.62), ("FLUSS", 0.66, 0.5), ("BUCHT", 0.78, 0.25),
                      ("STRAND", 0.72, 0.86), ("INSEL", 0.905, 0.84)]:
        d.text((S * x, S * y), txt, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(20, 40, 60))
    # Kompass
    cx, cy = S * 0.1, S * 0.1
    d.polygon([(cx, cy - 50), (cx - 16, cy), (cx + 16, cy)], fill=(235, 70, 70))
    d.polygon([(cx, cy + 50), (cx - 16, cy), (cx + 16, cy)], fill=(255, 255, 255))
    d.text((cx, cy - 72), "N", font=ImageFont.truetype(FB, 34), fill=(255, 255, 255), anchor="mm")
    return img

if __name__ == "__main__":
    p = panorama(); p.save("panorama.jpg", quality=90)
    k = karte(); k.save("karte.jpg", quality=90)
    p.resize((1200, 640)).save("/tmp/pan_s.jpg"); k.resize((500, 500)).save("/tmp/k_s.jpg")

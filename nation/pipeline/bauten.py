"""Bauten von Valmora – werden in allen Folgen wiederverwendet (Bildschirm-Koordinaten bei pan_view(2150))."""
import math

def lighthouse(d, x, base, prog, t, GOLD=(240, 190, 80)):
    hh = 820; top = base - hh * prog; tw = 150
    def clipbox(y0, y1): return max(y0, top), y1
    y0, y1 = clipbox(base - 220, base)
    if y1 > y0:
        d.rectangle([x - 260, y0, x - 40, y1], fill=(245, 240, 230))
        if top < base - 220:
            if top < base - 330:
                d.polygon([(x - 290, base - 220), (x - 150, base - 330), (x - 10, base - 220)], fill=(200, 70, 60))
            d.rectangle([x - 200, base - 150, x - 140, base - 80], fill=(120, 180, 230))
            d.rectangle([x - 110, base - 120, x - 60, base], fill=(130, 90, 60))
    for k in range(6):
        sy1 = base - k * 110; sy0 = sy1 - 110
        a, b = clipbox(sy0, sy1)
        if b > a:
            sh = 1 - k * 0.06
            d.polygon([(x - tw / 2 * sh, b), (x + tw / 2 * sh, b), (x + tw / 2 * (sh - 0.06), a), (x - tw / 2 * (sh - 0.06), a)],
                      fill=(235, 70, 70) if k % 2 == 0 else (250, 250, 250))
    if prog >= 0.82:
        d.rectangle([x - 60, base - 760, x + 60, base - 680], fill=(255, 240, 150))
        d.polygon([(x - 80, base - 760), (x, base - 820), (x + 80, base - 760)], fill=(200, 70, 60))
        if prog >= 1:
            for a in (-0.25, 0.25):
                ang = math.sin(t * 2) * 0.6 + a
                d.polygon([(x, base - 720), (x + 600 * math.cos(ang - 0.1), base - 720 + 600 * math.sin(ang - 0.1)),
                           (x + 600 * math.cos(ang + 0.1), base - 720 + 600 * math.sin(ang + 0.1))], fill=(255, 250, 200))
    if 0 < prog < 1:
        for yy in range(int(top), base, 60):
            d.line([(x - 110, yy), (x + 110, yy)], fill=(150, 110, 70), width=6)
        d.line([(x - 110, top), (x - 110, base)], fill=(150, 110, 70), width=6)
        d.line([(x + 110, top), (x + 110, base)], fill=(150, 110, 70), width=6)

def bootssteg(d, x0, y, length, prog, t):
    """Holzsteg vom Strand ins Meer, wird von links nach rechts gebaut; am Ende ein kleines Boot."""
    x1 = x0 + length * prog
    if prog > 0:
        # Pfähle
        px = x0 + 40
        while px < x1:
            d.rectangle([px - 9, y + 10, px + 9, y + 110], fill=(95, 65, 40))
            px += 90
        # Deck mit Planken
        d.rectangle([x0, y - 22, x1, y + 18], fill=(170, 120, 70))
        xx = x0
        while xx < x1:
            d.line([(xx, y - 22), (xx, y + 18)], fill=(120, 80, 45), width=4); xx += 26
        d.line([(x0, y + 18), (x1, y + 18)], fill=(100, 70, 40), width=6)
        # Geländer
        d.line([(x0, y - 70), (x1, y - 70)], fill=(140, 95, 55), width=8)
        px = x0
        while px <= x1:
            d.line([(px, y - 70), (px, y - 22)], fill=(140, 95, 55), width=8); px += 110
    if 0 < prog < 1:
        # Hammer-Funken
        for k in range(5):
            a = t * 9 + k * 1.3
            d.ellipse([x1 + math.cos(a) * 30 - 6, y - 40 + math.sin(a) * 30 - 6, x1 + math.cos(a) * 30 + 6, y - 40 + math.sin(a) * 30 + 6],
                      fill=(255, 230, 120))
    if prog >= 1:
        bx = x0 + length - 150; by = y + 60 + math.sin(t * 2.4) * 8
        d.polygon([(bx - 110, by), (bx + 110, by), (bx + 80, by + 50), (bx - 80, by + 50)], fill=(245, 245, 245))
        d.rectangle([bx - 110, by - 6, bx + 110, by + 6], fill=(30, 90, 150))
        d.line([(bx, by), (bx, by - 170)], fill=(110, 80, 50), width=8)
        d.polygon([(bx + 6, by - 165), (bx + 6, by - 20), (bx + 100, by - 30)], fill=(255, 196, 110))

def baeckerei(d, x, base, prog, t, font=None):
    """Kleine Bäckerei am Strand (Tag 2 · Teil 2, Wunsch aus den Kommentaren). x = linke Kante, base = Boden.
    Wird von unten nach oben gebaut; fertig mit Markise, Schild, Brot im Fenster und Rauch aus dem Schornstein."""
    w, hw = 330, 215
    top = base - (hw + 95) * prog
    if prog <= 0: return
    wy0 = max(base - hw, top)
    d.rectangle([x, wy0, x + w, base], fill=(250, 225, 180))
    if prog > 0.65:
        d.polygon([(x - 25, base - hw), (x + w / 2, base - hw - 95), (x + w + 25, base - hw)], fill=(160, 85, 50))
        d.rectangle([x + w - 85, base - hw - 100, x + w - 50, base - hw - 30], fill=(120, 70, 50))
    if prog > 0.4:
        d.rectangle([x + 30, base - 110, x + 95, base], fill=(130, 85, 50))
        d.rectangle([x + 130, base - 105, x + w - 30, base - 30], fill=(255, 235, 170), outline=(130, 85, 50), width=6)
        for k in range(4):
            bx = x + 145 + k * 40
            d.ellipse([bx, base - 72, bx + 36, base - 47], fill=(200, 130, 60))
    if prog >= 1:
        for k in range(6):
            d.rectangle([x + k * w / 6, base - hw, x + (k + 1) * w / 6, base - hw + 40],
                        fill=(230, 80, 80) if k % 2 == 0 else (255, 255, 255))
        if font is not None:
            d.rounded_rectangle([x + 15, base - hw + 50, x + w - 15, base - 118], radius=12, fill=(255, 250, 240),
                                outline=(160, 85, 50), width=4)
            d.text((x + w / 2, base - hw + 50 + (hw - 168) / 2), "BÄCKEREI", font=font, fill=(160, 85, 50), anchor="mm")
        for k in range(4):
            ph = (t * 0.6 + k * 0.25) % 1.0
            cx = x + w - 67 + math.sin(t * 2 + k) * 14 * ph
            cy = base - hw - 105 - ph * 120
            r = 12 + ph * 22
            g = int(235 - ph * 30)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(g, g, g))
    if 0 < prog < 1:
        for yy in range(int(top), base, 50):
            d.line([(x - 15, yy), (x + w + 15, yy)], fill=(150, 110, 70), width=5)
        d.line([(x - 15, top), (x - 15, base)], fill=(150, 110, 70), width=6)
        d.line([(x + w + 15, top), (x + w + 15, base)], fill=(150, 110, 70), width=6)

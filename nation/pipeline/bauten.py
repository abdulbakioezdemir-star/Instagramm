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

def fischerhuette(d, x, base, prog, t, font=None):
    """Fischerhütte am Strand (Tag 3 · Teil 1, Abstimmung '1'). x = linke Kante, base = Boden.
    Holzhütte auf Pfählen, Netz, Trockengestell mit Fischen. Wird von unten nach oben gebaut."""
    if prog <= 0: return
    w, hw, roof = 250, 120, 70
    wood, dark = (150, 105, 65), (100, 68, 40)
    top = base - (hw + roof + 20) * prog
    # Pfähle
    for px in (x + 15, x + w - 30):
        d.rectangle([px, max(base - 20, top), px + 15, base], fill=dark)
    wy0 = max(base - 20 - hw, top)
    if wy0 < base - 20:
        d.rectangle([x, wy0, x + w, base - 20], fill=wood)
        for yy in range(int(wy0) + 20, base - 20, 24):
            d.line([(x, yy), (x + w, yy)], fill=dark, width=3)
    if prog > 0.7:
        d.polygon([(x - 20, base - 20 - hw), (x + w / 2, base - 20 - hw - roof), (x + w + 20, base - 20 - hw)], fill=(70, 110, 150))
    if prog > 0.45:
        d.rectangle([x + 25, base - 115, x + 80, base - 20], fill=dark)
        d.rectangle([x + 120, base - 115, x + 210, base - 65], fill=(180, 220, 240), outline=dark, width=5)
    if prog >= 1:
        # Trockengestell mit Fischen rechts daneben
        gx = x + w + 40
        d.line([(gx, base), (gx, base - 110)], fill=dark, width=7)
        d.line([(gx + 110, base), (gx + 110, base - 110)], fill=dark, width=7)
        d.line([(gx - 5, base - 105), (gx + 115, base - 105)], fill=dark, width=6)
        for k in range(3):
            fx = gx + 18 + k * 36; sw = math.sin(t * 3 + k) * 4
            d.line([(fx, base - 105), (fx + sw, base - 85)], fill=(60, 60, 60), width=2)
            d.polygon([(fx + sw - 9, base - 85), (fx + sw + 9, base - 85), (fx + sw, base - 40)], fill=(150, 175, 195))
            d.polygon([(fx + sw - 9, base - 38), (fx + sw + 9, base - 38), (fx + sw, base - 50)], fill=(150, 175, 195))
        # Netz an der Wand
        for k in range(5):
            d.line([(x + 220 + k * 0, base - 130 + k * 20), (x + 245, base - 130 + k * 20)], fill=(230, 220, 190), width=2)
    if 0 < prog < 1:
        for yy in range(int(top), base, 45):
            d.line([(x - 15, yy), (x + w + 15, yy)], fill=(150, 110, 70), width=5)
        d.line([(x - 15, top), (x - 15, base)], fill=(150, 110, 70), width=6)
        d.line([(x + w + 15, top), (x + w + 15, base)], fill=(150, 110, 70), width=6)

def strandbar(d, x, base, prog, t, font=None):
    """Strandbar am Strand (Tag 3 · Teil 2, Abstimmung '1', Wunsch von till.ue). x = linke Kante, base = Boden.
    Theke mit Strohdach-Kante, gestreifter Sonnenschirm, zwei Hocker, Schild 'BAR'. Baut sich in Stufen auf."""
    if prog <= 0: return
    wood, dark, straw = (170, 120, 70), (105, 70, 40), (225, 190, 110)
    # Theke (Stufe 1)
    tw, th = 200, 80
    q = min(1, prog / 0.4)
    ty = base - th * q
    d.rectangle([x, ty, x + tw, base], fill=wood)
    for xx in range(x + 20, x + tw, 30):
        d.line([(xx, ty), (xx, base)], fill=dark, width=3)
    if prog > 0.35:
        d.rectangle([x - 10, base - th - 12, x + tw + 10, base - th], fill=dark)       # Thekenplatte
        for k in range(10):                                                              # Strohfransen
            fx = x - 8 + k * 22
            d.polygon([(fx, base - th), (fx + 22, base - th), (fx + 11, base - th + 22)], fill=straw)
    # Sonnenschirm (Stufe 2)
    if prog > 0.45:
        q2 = min(1, (prog - 0.45) / 0.3)
        px = x + tw + 60
        top = base - 190 * q2
        d.line([(px, base), (px, top)], fill=(240, 240, 240), width=7)
        if q2 >= 1:
            sway = math.sin(t * 2) * 3
            r = 95
            cols = [(235, 80, 80), (255, 255, 255)]
            for k in range(6):
                a0, a1 = -r + k * (2 * r / 6), -r + (k + 1) * (2 * r / 6)
                d.polygon([(px + sway, top - 45), (px + a0, top + 5), (px + a1, top + 5)], fill=cols[k % 2])
    # Hocker (Stufe 3)
    if prog > 0.75:
        for hx in (x + 40, x + 130):
            d.line([(hx + 15, base - 55), (hx + 15, base)], fill=dark, width=6)
            d.ellipse([hx - 5, base - 65, hx + 35, base - 48], fill=(235, 80, 80))
    # Schild + Getränk (fertig)
    if prog >= 1:
        d.rounded_rectangle([x + 40, base - th - 70, x + 160, base - th - 18], radius=12, fill=(255, 245, 210), outline=dark, width=4)
        if font: d.text((x + 100, base - th - 44), "BAR", font=font, fill=dark, anchor="mm")
        gx = x + 165; gy = base - th - 12
        d.polygon([(gx, gy - 40), (gx + 26, gy - 40), (gx + 20, gy), (gx + 6, gy)], fill=(255, 170, 60), outline=(255, 255, 255))
        d.line([(gx + 18, gy - 40), (gx + 28, gy - 58)], fill=(90, 200, 120), width=4)
    if 0 < prog < 1:
        for yy in range(int(base - 200 * prog), base, 45):
            d.line([(x - 15, yy), (x + tw + 15, yy)], fill=(150, 110, 70), width=5)

def mauer(d, x, base, prog, t, font=None, steine=3):
    """Mini-Mauer am Strand (Tag 4 · Teil 1, Abstimmung '3', Wunsch von seal.medusa). x = linke Kante, base = Boden.
    Nur drei Steinreihen hoch (Kasse reichte nicht für mehr). Reihen kommen nacheinander dazu."""
    if prog <= 0: return
    sw, sh, n = 50, 30, 4                      # Stein-Breite/-Höhe, Steine pro Reihe
    stone, dark = (175, 170, 160), (110, 105, 98)
    rows = min(steine, int(prog * steine + 0.999))
    for r in range(rows):
        q = 1.0 if r < rows - 1 or prog >= 1 else min(1, (prog * steine - r) * 1.2)
        off = (sw // 2) if r % 2 else 0
        y1 = base - r * sh; y0 = y1 - sh
        drop = (1 - q) * -60
        for k in range(n + (1 if r % 2 else 0)):
            x0 = x + k * sw - off; x1 = x0 + sw
            x0 = max(x0, x); x1 = min(x1, x + n * sw)
            if x1 - x0 < 8: continue
            d.rectangle([x0 + 2, y0 + drop + 2, x1 - 2, y1 + drop - 2], fill=stone, outline=dark, width=3)
    if prog >= 1 and font:
        d.rounded_rectangle([x + n * sw + 15, base - 75, x + n * sw + 115, base - 35], radius=8, fill=(255, 245, 210), outline=dark, width=3)
        d.text((x + n * sw + 65, base - 55), "MAUER", font=font, fill=dark, anchor="mm")
        d.line([(x + n * sw + 65, base - 35), (x + n * sw + 65, base)], fill=dark, width=4)

def katze(d, x, base, s=1.0, hop=0.0, col=(60, 60, 70)):
    """Kleine Katze (Seitenansicht), läuft nach rechts. hop = Höhe über Boden."""
    y = base - hop
    d.ellipse([x - 30 * s, y - 40 * s, x + 30 * s, y - 12 * s], fill=col)               # Körper
    d.ellipse([x + 18 * s, y - 58 * s, x + 46 * s, y - 30 * s], fill=col)               # Kopf
    d.polygon([(x + 22 * s, y - 52 * s), (x + 26 * s, y - 68 * s), (x + 32 * s, y - 55 * s)], fill=col)
    d.polygon([(x + 34 * s, y - 55 * s), (x + 40 * s, y - 68 * s), (x + 44 * s, y - 50 * s)], fill=col)
    d.ellipse([x + 34 * s, y - 49 * s, x + 39 * s, y - 44 * s], fill=(240, 220, 90))     # Auge
    for lx in (-22, -10, 10, 20):
        d.line([(x + lx * s, y - 18 * s), (x + lx * s, y)], fill=col, width=max(2, int(6 * s)))
    d.line([(x - 28 * s, y - 30 * s), (x - 48 * s, y - 60 * s)], fill=col, width=max(2, int(7 * s)))  # Schwanz

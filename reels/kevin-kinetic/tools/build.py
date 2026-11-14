"""Kinetic-type edit (see STIL-REFERENZ.md): one word per cut, black/white swap on every cut,
stacked pairs, typing on "potenzial", gold only on key words. Writes index.html."""
import json, random
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype(str(HERE / "fonts" / "InterDisplay-Black.otf"), 100)
MAXW = 960
DUR = 18.0

def fit(text, size):
    w = FONT.getlength(text) * size / 100 * 0.96          # letter-spacing -0.04em
    return min(size, int(size * MAXW / max(w, 1)))

# (time, bg, lines)   line = (text, size, style)   style: None | "gold" | "dot"
C = [
 (0.00, "w", [("in", 170, None)]),
 (0.16, "b", [("in", 130, None), ("dir", 380, None)]),
 (0.34, "w", [("steckt", 320, None)]),
 (0.72, "b", [("mehr,", 440, None)]),
 (1.04, "w", [("als", 180, None)]),
 (1.32, "b", [("als du", 180, None)]),
 (1.54, "w", [("als du", 130, None), ("denkst.", 340, None)]),
 (2.42, "b", [("ein", 180, None)]),
 (2.60, "w", [("ein", 130, None), ("funke", 390, "dot")]),
 (3.52, "b", [("druck.", 380, None)]),
 (4.38, "w", [("zweifel.", 360, None)]),
 (5.40, "b", [("angst.", 420, None)]),
 (6.32, "w", [("doch", 200, None)]),
 (6.48, "b", [("doch ein", 180, None)]),
 (6.86, "w", [("doch ein", 130, None), ("funke", 390, None)]),
 (7.34, "b", [("genügt.", 380, "gold")]),
 (8.20, "w", [("po", 440, None)]),
 (8.36, "b", [("poten", 400, None)]),
 (8.52, "w", [("potenzi", 340, None)]),
 (8.70, "b", [("potenzial", 320, "gold")]),
 (8.88, "w", [("potenzial", 150, None), ("entfachen.", 300, "gold")]),
 (9.76, "b", [("klarheit.", 340, None)]),
 (10.70, "w", [("fokus.", 420, None)]),
 (11.70, "b", [("stärke.", 400, "gold")]),
 (12.64, "w", "LOGO"),
 (13.24, "b", "LOGO"),
 (13.98, "w", [("dein", 200, None)]),
 (14.24, "b", [("dein", 130, None), ("mental", 360, None)]),
 (14.66, "w", [("mental", 150, None), ("coach", 420, "dot")]),
 (15.30, "b", "END"),
]

rng = random.Random(4)
cards, js = [], []
for i, (t, bg, lines) in enumerate(C):
    t1 = C[i + 1][0] if i + 1 < len(C) else DUR
    cid = f"c{i}"
    dust = "".join(f'<i style="left:{rng.uniform(30,1050):.0f}px;top:{rng.uniform(80,1840):.0f}px;opacity:{rng.uniform(.15,.5):.2f};width:{rng.choice([2,3,3,4])}px;height:{rng.choice([2,3,3,4])}px"></i>' for _ in range(14))
    if lines == "LOGO":
        body = f'<div id="{cid}x"><img class="logo{" inv" if bg == "w" else ""}" src="ui/kn-logo.png" alt="Kevin Nsimba" style="width:{560 if bg == "w" else 760}px"></div>'
    elif lines == "END":
        body = (f'<img class="logo" id="{cid}x" src="ui/kn-logo.png" alt="Kevin Nsimba" style="width:560px">'
                f'<div class="role" id="{cid}r">dein <span class="gold-b">mental coach.</span></div>'
                f'<div class="claim" id="{cid}c">train the mind.<br><span class="gold-b">change the game.</span></div>'
                f'<div class="handle" id="{cid}h">@kevnsimba</div>')
    else:
        rows = []
        for k, (txt, size, style) in enumerate(lines):
            s = fit(txt + ("." if style == "dot" else ""), size)
            cls = "ln" + (f" gold-{bg}" if style == "gold" else "")
            inner = txt + (f'<span class="gold-{bg}">.</span>' if style == "dot" else "")
            last = ' id="%sx"' % cid if k == len(lines) - 1 else ""
            rows.append(f'<div class="{cls}"{last} style="font-size:{s}px">{inner}</div>')
        body = '<div class="stack">' + "".join(rows) + "</div>"
    cards.append(f'<div class="card {bg}" id="{cid}"><div class="dust">{dust}</div>{body}</div>')
    js.append(f'tl.set("#{cid}", {{ visibility: "visible" }}, {t:.3f}); tl.set("#{cid}", {{ visibility: "hidden" }}, {t1:.3f});')
    d = -1 if i % 2 else 1
    if lines == "END":
        js.append(f'tl.fromTo("#{cid}x", {{ scale: 1.15, filter: "blur(12px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }}, {t:.3f});')
        js.append(f'tl.fromTo(["#{cid}r", "#{cid}c", "#{cid}h"], {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out", stagger: 0.38 }}, {t + 0.3:.3f});')
    else:
        js.append(f'tl.fromTo("#{cid}x", {{ x: {70 * d}, filter: "blur(10px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.1, ease: "power3.out" }}, {t:.3f});')

html = (HERE / "tools" / "index.tpl.html").read_text()
html = html.replace("{CARDS}", "\n      ".join(cards)).replace("{JS}", "\n      ".join(js)).replace("{DUR}", str(DUR))
(HERE / "index.html").write_text(html)
print("ok", len(C), "cards")

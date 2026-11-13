"""Builds index.html from tools/index.tpl.html: logo, embers, grain, sfx."""
import random, re
from pathlib import Path
import numpy as np, cv2
HERE = Path(__file__).resolve().parent.parent
tpl = (HERE / "tools" / "index.tpl.html").read_text()
logo = (HERE / "ui" / "logo.svg").read_text()
rng = random.Random(7)
emb, js = [], []
for i in range(48):
    x, sz, d, delay = rng.uniform(20, 1060), rng.uniform(4, 10), rng.uniform(7, 13), rng.uniform(0, 12)
    op = rng.uniform(.25, .8)
    emb.append(f'<div class="ember" id="e{i}" style="left:{x:.0f}px;top:0;width:{sz:.1f}px;height:{sz:.1f}px"></div>')
    drift = rng.uniform(-90, 90)
    # each ember rises from below the frame; start offset spreads them over the screen at t=0
    ph = (delay % d) / d                      # where in its rise the ember is at t=0
    y0 = 2000 - 2060 * ph
    rest = d * (1 - ph)
    js.append(f'tl.fromTo("#e{i}", {{ y: {y0:.0f}, x: {drift*ph:.0f}, opacity: {op:.2f} }}, {{ y: -60, x: {drift:.0f}, duration: {rest:.2f}, ease: "none" }}, 0);')
    js.append(f'tl.fromTo("#e{i}", {{ y: 2000, x: 0 }}, {{ y: -60, x: {drift:.0f}, duration: {d:.2f}, ease: "none", repeat: 2, immediateRender: false }}, {rest:.2f});')
brand = "".join(f'<span class="bl" style="display:inline-block">{c if c != " " else "&nbsp;"}</span>' for c in "BAKI MOTION")
sfx = []
for i, (t, f, v) in enumerate([(2.78, "whoosh", .22), (4.25, "whoosh", .3), (8.98, "whoosh-short", .25), (11.45, "whoosh-short", .22), (13.88, "whoosh-short", .25)]):
    sfx.append(f'<audio id="sx{i}" class="clip" src="sfx/{f}.mp3" data-start="{t}" data-duration="0.6" data-track-index="{10+i}" data-volume="{v}"></audio>')
out = tpl.replace("{LOGO}", logo).replace("{EMBERS}", "\n          ".join(emb)).replace("{EMBER_JS}", "\n      ".join(js)).replace("{BRAND}", brand).replace("{SFX}", "\n      ".join(sfx))
(HERE / "index.html").write_text(out)
g = np.random.default_rng(3).normal(128, 50, (256, 256)).clip(0, 255).astype(np.uint8)
cv2.imwrite(str(HERE / "ui" / "grain.png"), g)
print("ok")

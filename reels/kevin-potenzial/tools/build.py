"""Builds index.html from tools/index.tpl.html (embers, grain)."""
import random
from pathlib import Path
import numpy as np, cv2
HERE = Path(__file__).resolve().parent.parent
tpl = (HERE / "tools" / "index.tpl.html").read_text()
rng = random.Random(11)
emb, js = [], []
for i in range(30):
    x, sz, d, delay = rng.uniform(40, 1040), rng.uniform(3, 7), rng.uniform(8, 14), rng.uniform(0, 14)
    op, drift = rng.uniform(.2, .6), rng.uniform(-80, 80)
    emb.append(f'<div class="ember" id="em{i}" data-o="{op:.2f}" style="left:{x:.0f}px;width:{sz:.1f}px;height:{sz:.1f}px;opacity:0"></div>')
    ph = (delay % d) / d
    rest = d * (1 - ph)
    js.append(f'tl.fromTo("#em{i}", {{ y: {2000 - 2080 * ph:.0f}, x: {drift * ph:.0f} }}, {{ y: -80, x: {drift:.0f}, duration: {rest:.2f}, ease: "none" }}, 0);')
    js.append(f'tl.fromTo("#em{i}", {{ y: 2000, x: 0 }}, {{ y: -80, x: {drift:.0f}, duration: {d:.2f}, ease: "none", repeat: 2, immediateRender: false }}, {rest:.2f});')
out = tpl.replace("{EMBERS}", "\n          ".join(emb)).replace("{EMBER_JS}", "\n      ".join(js))
(HERE / "index.html").write_text(out)
g = np.random.default_rng(5).normal(128, 50, (256, 256)).clip(0, 255).astype(np.uint8)
cv2.imwrite(str(HERE / "ui" / "grain.png"), g)
print("ok")

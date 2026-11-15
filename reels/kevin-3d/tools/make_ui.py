"""Renders Kevin's profile screen (from reels/kevin-slate/tools/build.py) to textures for the 3D phone."""
import importlib.util, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("slate", HERE.parent / "kevin-slate" / "tools" / "build.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
css = m.CSS.replace("url(fonts/", f"url({(HERE / 'fonts').as_uri()}/").replace("url(ui/", f"url({(HERE / 'ui').as_uri()}/")
ph = m.phone().replace("src='ui/", f"src='{(HERE / 'ui').as_uri()}/")
page = HERE / "build" / "screen.html"
page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{css} #ph{{left:0;top:0}} #spec{{display:none}} #pbody{{display:none}} .tile, #avd, .ring {{visibility:hidden}}"
                f" .hide .btn, .hide .hl, .hide .tab, .hide .tabl {{ visibility:hidden }}</style></head><body style='background:#000'>{ph}</body></html>")
js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage({{ viewport: {{ width: 600, height: 1200 }}, deviceScaleFactor: 2 }});
  await p.goto('{page.as_uri()}'); await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.locator('#scr').screenshot({{ path: '{HERE}/build/scr_full.png' }});
  await p.evaluate(() => document.getElementById('scr').classList.add('hide'));
  await p.locator('#scr').screenshot({{ path: '{HERE}/build/scr_base.png' }});
  await b.close();
}})();
"""
subprocess.run(["node", "-e", js], check=True)
full = Image.open(HERE / "build/scr_full.png").convert("RGBA"); base = Image.open(HERE / "build/scr_base.png").convert("RGBA")
S = full.width / 560
def rr(img, r):
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    img.putalpha(mk); return img
rr(base, int(76 * S)).save(HERE / "ui/screen.png")
panels = {"btns": (26, 492, 534, 564), "hls": (16, 572, 544, 712), "tabs": (0, 708, 560, 756)}
meta = {}
for k, (x0, y0, x1, y1) in panels.items():
    full.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S))).save(HERE / f"ui/{k}.png")
    meta[k] = [x0, y0, x1, y1]
for n in ["suit", "restaurant", "mentale", "player", "sp", "amator"]:
    im = Image.open(HERE / f"ui/posts/{n}.jpg"); w, h = im.size
    im.crop((0, (h - w) // 2, w, (h - w) // 2 + w)).resize((512, 512), Image.LANCZOS).save(HERE / f"ui/sq_{n}.jpg", quality=90)
json.dump(meta, open(HERE / "ui/panels.json", "w"))
print("ok", full.size)

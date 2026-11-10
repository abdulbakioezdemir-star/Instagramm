"""Draws the reference objects of "42 Falten bis zum Mond". Each SVG's viewBox height is the object's real height,
so the HTML can size it purely from metres."""
import os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I = os.path.join(ROOT, "assets", "img")
os.makedirs(I, exist_ok=True)
w = lambda n, s: open(os.path.join(I, n), "w").write(s)

# coffee mug, 10 cm tall
w("cup.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130 100" width="130" height="100">
<defs><linearGradient id="c" x1="0" x2="1"><stop offset="0" stop-color="#8f2f24"/><stop offset=".35" stop-color="#d9563f"/><stop offset=".7" stop-color="#b8432f"/><stop offset="1" stop-color="#6e2219"/></linearGradient></defs>
<path d="M100 28 q30 0 30 24 q0 26 -32 28" fill="none" stroke="#9c3627" stroke-width="9"/>
<path d="M8 6 L102 6 L96 92 Q95 100 86 100 L24 100 Q15 100 14 92 Z" fill="url(#c)"/>
<ellipse cx="55" cy="6" rx="47" ry="5" fill="#4a1a12"/><ellipse cx="55" cy="7" rx="42" ry="3.4" fill="#2b140c"/>
<path d="M22 14 L26 88" stroke="#fff" stroke-opacity=".22" stroke-width="5" stroke-linecap="round"/></svg>""")

# family house, 13 m to the ridge
w("house.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 13" width="140" height="130">
<rect x="1.5" y="6" width="11" height="7" fill="#d8cdb8"/><rect x="1.5" y="6" width="3" height="7" fill="#c2b59c"/>
<polygon points="0.5,6.4 7,1 13.5,6.4" fill="#8a3b2c"/><polygon points="0.5,6.4 7,1 7,6.4" fill="#6f2e22"/>
<rect x="9.6" y="1.8" width="1.2" height="2.6" fill="#6b5b4d"/>
<g fill="#5b7a9a"><rect x="3" y="7.4" width="2" height="1.8"/><rect x="9" y="7.4" width="2" height="1.8"/><rect x="3" y="10.2" width="2" height="1.6"/></g>
<rect x="6.3" y="9.6" width="1.6" height="3.4" fill="#5a3b28"/></svg>""")

# Burj Khalifa, 828 m: a stepped needle
steps = [(0, 70), (120, 58), (240, 46), (360, 36), (460, 26), (560, 18), (640, 11), (700, 6), (760, 2.5), (828, 0.6)]
pts_l, pts_r = [], []
for i in range(len(steps) - 1):
    h0, wd = steps[i]; h1 = steps[i + 1][0]
    pts_l += [(-wd, 828 - h0), (-wd, 828 - h1)]
    pts_r += [(wd, 828 - h0), (wd, 828 - h1)]
poly = pts_l + [(0, 0)] + list(reversed(pts_r))
pstr = " ".join(f"{x + 80:.1f},{y:.1f}" for x, y in poly)
w("burj.svg", f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 828" width="160" height="828">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#6d7f90"/><stop offset=".45" stop-color="#d7e2ea"/><stop offset=".55" stop-color="#9fb2c2"/><stop offset="1" stop-color="#4c5b69"/></linearGradient></defs>
<polygon points="{pstr}" fill="url(#g)"/></svg>""")

# Mount Everest, 8849 m high; drawn 22 km wide
random.seed(4)
ridge = [(0, 8849 * 0.08)]
for x in range(1, 22):
    peak = 1 - abs(x - 11) / 11
    ridge.append((x * 1000, 8849 * (0.08 + 0.92 * peak ** 1.25) * (0.9 + random.random() * 0.12) if x != 11 else 8849))
ridge.append((22000, 8849 * 0.06))
top = " ".join(f"{x},{8849 - y:.0f}" for x, y in ridge)
snow = " ".join(f"{x},{8849 - y:.0f}" for x, y in ridge if y > 8849 * 0.62)
w("everest.svg", f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22000 8849" width="2200" height="885" preserveAspectRatio="none">
<defs><linearGradient id="m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6c7480"/><stop offset=".5" stop-color="#3c434d"/><stop offset="1" stop-color="#262b33"/></linearGradient></defs>
<polygon points="0,8849 {top} 22000,8849" fill="url(#m)"/>
<polygon points="7600,{8849 - 8849 * 0.64:.0f} {snow} 14800,{8849 - 8849 * 0.64:.0f}" fill="#eef2f6" opacity=".92"/>
<polygon points="11000,0 11000,8849 22000,8849 22000,{8849 - 8849 * 0.06:.0f}" fill="#000" opacity=".18"/></svg>""")

# ISS icon (drawn as a symbol; the real station is 109 m wide)
w("iss.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 90" width="200" height="90">
<g fill="#c7a24a" stroke="#6d5a26" stroke-width="2"><rect x="4" y="10" width="34" height="70"/><rect x="42" y="10" width="34" height="70"/><rect x="124" y="10" width="34" height="70"/><rect x="162" y="10" width="34" height="70"/></g>
<rect x="76" y="40" width="48" height="10" fill="#dfe5ea"/><rect x="88" y="26" width="24" height="38" rx="6" fill="#eef2f5"/><rect x="94" y="14" width="12" height="62" fill="#c9d1d8"/></svg>""")

# the Moon, lit from the upper left, with craters
random.seed(7)
craters = "".join(
    f'<circle cx="{random.uniform(80, 920):.0f}" cy="{random.uniform(80, 920):.0f}" r="{random.choice([14, 20, 28, 40, 60]) * random.uniform(.6, 1.3):.0f}" fill="#000" opacity="{random.uniform(.08, .2):.2f}"/>'
    for _ in range(46))
w("moon.svg", f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
<defs><radialGradient id="l" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#f2efe8"/><stop offset=".55" stop-color="#b9b5ad"/><stop offset=".9" stop-color="#4f4c48"/><stop offset="1" stop-color="#1d1c1b"/></radialGradient>
<clipPath id="k"><circle cx="500" cy="500" r="498"/></clipPath></defs>
<circle cx="500" cy="500" r="498" fill="url(#l)"/>
<g clip-path="url(#k)"><path d="M180 300 q120 -80 260 -20 q100 60 40 160 q-90 120 -230 60 q-110 -60 -70 -200z" fill="#6b6862" opacity=".35"/>
<path d="M560 560 q140 -40 220 60 q40 120 -90 150 q-150 10 -170 -90z" fill="#6b6862" opacity=".3"/>{craters}
<circle cx="500" cy="500" r="498" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="40"/></g></svg>""")

# Earth seen from space
w("earth.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
<defs><radialGradient id="o" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#4fa3e8"/><stop offset=".6" stop-color="#1d5fa8"/><stop offset="1" stop-color="#06203f"/></radialGradient>
<radialGradient id="a" cx=".5" cy=".5" r=".5"><stop offset=".93" stop-color="#7cc4ff" stop-opacity="0"/><stop offset="1" stop-color="#9fd6ff" stop-opacity=".7"/></radialGradient>
<clipPath id="k"><circle cx="500" cy="500" r="490"/></clipPath></defs>
<circle cx="500" cy="500" r="490" fill="url(#o)"/>
<g clip-path="url(#k)" fill="#3f8a4a"><path d="M260 210 q90 -40 160 20 q30 70 -30 120 q-40 70 -110 40 q-70 -40 -60 -110z"/><path d="M520 380 q110 -30 190 40 q60 90 -20 170 q-80 70 -150 10 q-60 -80 -20 -220z"/><path d="M300 600 q60 -20 90 40 q10 90 -60 120 q-60 -10 -60 -80z"/></g>
<g clip-path="url(#k)" fill="#fff" opacity=".55"><path d="M150 420 q120 -40 260 0 q-120 30 -260 0z"/><path d="M480 250 q140 -30 260 10 q-140 20 -260 -10z"/><path d="M420 720 q160 -30 300 10 q-160 25 -300 -10z"/></g>
<circle cx="500" cy="500" r="500" fill="url(#a)"/></svg>""")

# a cloud deck
w("clouds.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300">
<g fill="#ffffff"><ellipse cx="160" cy="200" rx="160" ry="70" opacity=".85"/><ellipse cx="380" cy="170" rx="190" ry="90" opacity=".9"/><ellipse cx="640" cy="210" rx="200" ry="70" opacity=".8"/>
<ellipse cx="900" cy="180" rx="200" ry="85" opacity=".9"/><ellipse cx="1110" cy="215" rx="140" ry="60" opacity=".8"/></g></svg>""")
print("ok")

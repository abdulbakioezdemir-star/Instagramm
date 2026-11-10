"""Draws the film's SVG assets: chess pieces in three materials, the crown, the board, the office."""
import os, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "assets", "pieces"); I = os.path.join(ROOT, "assets", "img")
os.makedirs(P, exist_ok=True); os.makedirs(I, exist_ok=True)

MAT = {
  "white": ["#8a8478", "#f6f2ea", "#ddd6c8", "#77716a", "#ffffff"],
  "black": ["#030304", "#4a4e57", "#17191d", "#010102", "#8a90a0"],
  "gold":  ["#5e3f0c", "#ffe6a3", "#d4a446", "#4a300a", "#fff3cf"],
}
BASE = "M30 400 Q30 372 50 366 L150 366 Q170 372 170 400 Z M44 366 Q46 350 62 346 L138 346 Q154 350 156 366 Z"
SHAPES = {
 "pawn":   BASE + " M70 346 Q76 300 84 258 L116 258 Q124 300 130 346 Z M64 262 Q100 244 136 262 L136 270 Q100 256 64 270 Z M100 170 a46 46 0 1 0 0.1 0 Z",
 "rook":   BASE + " M62 346 L70 190 L130 190 L138 346 Z M54 196 L146 196 L146 180 L54 180 Z M54 182 L54 120 L76 120 L76 144 L90 144 L90 120 L110 120 L110 144 L124 144 L124 120 L146 120 L146 182 Z",
 "bishop": BASE + " M66 346 Q74 270 84 230 L116 230 Q126 270 134 346 Z M62 236 Q100 218 138 236 L138 244 Q100 230 62 244 Z M100 82 Q146 130 136 180 Q128 218 100 224 Q72 218 64 180 Q56 130 100 82 Z M100 54 a16 16 0 1 0 0.1 0 Z",
 "knight": BASE + " M60 346 Q60 280 84 240 Q60 236 48 214 Q40 196 58 182 L96 150 Q92 120 110 96 L118 72 L128 98 Q160 120 162 190 Q164 260 146 346 Z",
 "queen":  BASE + " M62 346 Q72 260 82 214 L118 214 Q128 260 138 346 Z M56 220 Q100 200 144 220 L144 230 Q100 212 56 230 Z M60 206 L44 112 L72 160 L84 96 L100 156 L116 96 L128 160 L156 112 L140 206 Q100 192 60 206 Z M100 70 a14 14 0 1 0 0.1 0 Z",
 "king":   BASE + " M60 346 Q70 250 80 200 L120 200 Q130 250 140 346 Z M52 206 Q100 186 148 206 L148 216 Q100 198 52 216 Z M58 194 Q54 150 66 128 L134 128 Q146 150 142 194 Q100 180 58 194 Z",
}
def piece(kind, mat):
    a, hi, mid, d, rim = MAT[mat]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{a}"/><stop offset=".34" stop-color="{hi}"/><stop offset=".62" stop-color="{mid}"/><stop offset="1" stop-color="{d}"/></linearGradient>
<linearGradient id="v" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient></defs>
<path d="{SHAPES[kind]}" fill="url(#g)" fill-rule="nonzero"/>
<path d="{SHAPES[kind]}" fill="url(#v)"/>
<path d="{SHAPES[kind]}" fill="none" stroke="{rim}" stroke-opacity=".35" stroke-width="2"/>
</svg>'''
for k in SHAPES:
    for m in MAT:
        open(os.path.join(P, f"{k}-{m}.svg"), "w").write(piece(k, m))

# crown + cross that sit on the gold king (separate so it can fly off)
a, hi, mid, d, rim = MAT["gold"]
open(os.path.join(P, "crown.svg"), "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{a}"/><stop offset=".34" stop-color="{hi}"/><stop offset=".62" stop-color="{mid}"/><stop offset="1" stop-color="{d}"/></linearGradient></defs>
<path d="M40 190 L30 110 L64 140 L80 90 L100 132 L120 90 L136 140 L170 110 L160 190 Z" fill="url(#g)" stroke="{rim}" stroke-opacity=".5" stroke-width="2"/>
<rect x="38" y="176" width="124" height="18" rx="4" fill="{d}"/>
<circle cx="70" cy="184" r="5" fill="#b3202a"/><circle cx="100" cy="184" r="6" fill="#1d6fb3"/><circle cx="130" cy="184" r="5" fill="#b3202a"/>
<rect x="92" y="20" width="16" height="74" rx="3" fill="url(#g)"/><rect x="74" y="38" width="52" height="15" rx="3" fill="url(#g)"/>
</svg>''')

# board texture, 8x8 marble with a wooden frame (1000 x 1000, squares 115, frame 40)
sq = 115; fr = 40
cells = []
for r in range(8):
    for f in range(8):
        dark = (r + f) % 2 == 1
        cells.append(f'<rect x="{fr+f*sq}" y="{fr+r*sq}" width="{sq}" height="{sq}" fill="{"url(#dk)" if dark else "url(#lt)"}"/>')
veins = "".join(f'<path d="M{fr+40+i*130} {fr} q{60} {300} {-30} {520} t{40} {400}" stroke="#ffffff" stroke-opacity=".06" stroke-width="3" fill="none"/>' for i in range(7))
open(os.path.join(I, "board.svg"), "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
<defs><linearGradient id="lt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6dfd0"/><stop offset="1" stop-color="#c9c0ae"/></linearGradient>
<linearGradient id="dk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2d2b30"/><stop offset="1" stop-color="#18171b"/></linearGradient>
<linearGradient id="wd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2516"/><stop offset="1" stop-color="#1e120a"/></linearGradient></defs>
<rect width="1000" height="1000" fill="url(#wd)"/>
{''.join(cells)}{veins}
<rect x="{fr}" y="{fr}" width="{8*sq}" height="{8*sq}" fill="none" stroke="#0e0905" stroke-width="4"/>
</svg>''')

# office at night, one-point perspective; screen positions are exported for the HTML generator
VPX, VPY = 540, 760
screens = []
desks = []
for d in [3.4, 2.3, 1.4, 0.65]:
    s = 1 / (1 + d * 0.75)
    top = VPY + 1000 * s
    for c in [-1.5, -0.5, 0.5, 1.5]:
        cx = VPX + c * 380 * s
        w, h = 270 * s, 170 * s
        screens.append((round(cx - w / 2, 1), round(top - 18 * s - h, 1), round(w, 1), round(h, 1), round(s, 3)))
    desks.append((s, top))
desk_svg = ""
for s, top in desks:
    x0, x1 = VPX - 800 * s, VPX + 800 * s
    desk_svg += f'<polygon points="{x0},{top} {x1},{top} {x1+90*s},{top+70*s} {x0-90*s},{top+70*s}" fill="#2a2f36"/>'
    desk_svg += f'<rect x="{x0-90*s}" y="{top+70*s}" width="{(x1-x0)+180*s}" height="{120*s}" fill="#15181d"/>'
    for (sx, sy, w, h, ss) in [q for q in screens if abs(q[4] - s) < 1e-3]:
        desk_svg += f'<rect x="{sx-6*ss}" y="{sy-6*ss}" width="{w+12*ss}" height="{h+12*ss}" rx="{6*ss}" fill="#0b0d10"/>'
        desk_svg += f'<rect x="{sx+w/2-8*ss}" y="{sy+h}" width="{16*ss}" height="{24*ss}" fill="#0b0d10"/>'
        desk_svg += f'<path d="M{sx+w/2-40*ss} {top+150*s} q{40*ss} {-90*ss} {80*ss} 0 v{60*ss} h{-80*ss}z" fill="#101317"/>'
city = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{1920}" fill="#0c1220"/>' for x, y, w in [(200,520,90),(300,470,70),(380,560,110),(500,430,80),(590,500,120),(720,450,70),(800,540,90)])
lights = "".join(f'<rect x="{210+(i*37)%600}" y="{480+(i*53)%240}" width="8" height="10" fill="#e8c27a" opacity=".6"/>' for i in range(40))
open(os.path.join(I, "office.svg"), "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
<defs><linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1f26"/><stop offset="1" stop-color="#0c0e12"/></linearGradient>
<linearGradient id="cl" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#14171c"/><stop offset="1" stop-color="#090a0d"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060912"/><stop offset="1" stop-color="#18223a"/></linearGradient></defs>
<rect width="1080" height="1920" fill="#0d0f13"/>
<polygon points="0,0 1080,0 1080,420 {VPX+260},{VPY-120} {VPX-260},{VPY-120} 0,420" fill="url(#cl)"/>
<g fill="#3a4250" opacity=".7"><polygon points="300,60 780,60 700,170 380,170"/><polygon points="420,300 660,300 630,350 450,350"/><polygon points="480,430 600,430 590,455 490,455"/></g>
<rect x="{VPX-260}" y="{VPY-120}" width="520" height="300" fill="url(#sky)"/>
<svg x="{VPX-260}" y="{VPY-120}" width="520" height="300" viewBox="200 400 700 420" preserveAspectRatio="none">{city}{lights}</svg>
<g stroke="#0d0f13" stroke-width="10"><line x1="{VPX-130}" y1="{VPY-120}" x2="{VPX-130}" y2="{VPY+180}"/><line x1="{VPX}" y1="{VPY-120}" x2="{VPX}" y2="{VPY+180}"/><line x1="{VPX+130}" y1="{VPY-120}" x2="{VPX+130}" y2="{VPY+180}"/></g>
<polygon points="0,420 {VPX-260},{VPY-120} {VPX-260},{VPY+180} 0,1500" fill="#14171c"/>
<polygon points="1080,420 {VPX+260},{VPY-120} {VPX+260},{VPY+180} 1080,1500" fill="#12151a"/>
<polygon points="0,1500 {VPX-260},{VPY+180} {VPX+260},{VPY+180} 1080,1500 1080,1920 0,1920" fill="url(#fl)"/>
{desk_svg}
</svg>''')

# his desk in the foreground: desk edge, monitor, the man from behind
open(os.path.join(I, "his-desk.svg"), "w").write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
<polygon points="-60,1560 760,1500 820,1600 -60,1700" fill="#2e333b"/>
<rect x="-60" y="1650" width="900" height="300" fill="#13161a"/>
<rect x="60" y="1060" width="560" height="360" rx="14" fill="#07080a"/>
<rect x="320" y="1420" width="40" height="80" fill="#07080a"/><rect x="250" y="1490" width="180" height="20" rx="6" fill="#07080a"/>
<path d="M600 1920 L600 1700 Q600 1560 700 1520 Q760 1500 790 1470 Q760 1450 752 1400 Q744 1300 820 1280 Q900 1270 912 1360 Q920 1420 880 1470 Q910 1500 970 1520 Q1080 1560 1080 1700 L1080 1920 Z" fill="#050608"/>
<path d="M752 1400 Q744 1300 820 1280 Q900 1270 912 1360" fill="none" stroke="#7fe3a8" stroke-opacity=".35" stroke-width="5"/>
</svg>''')
import json
json.dump({"screens": screens}, open(os.path.join(ROOT, "tools", "screens.json"), "w"))
print("ok", len(screens))

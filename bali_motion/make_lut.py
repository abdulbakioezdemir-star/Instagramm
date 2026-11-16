"""Generates the 'Bali Golden Hour' colour-grading LUT (.cube, 33^3).

Usable in Premiere/DaVinci/After Effects/CapCut and with ffmpeg lut3d.
- S-curve contrast with soft highlight roll-off and lifted blacks
- Split toning: teal shadows, warm golden highlights
- Vibrance: boosts muted colours more than already saturated ones
- Greens shifted slightly towards lush emerald, skin/orange protected
"""
import numpy as np

S = 33
g = np.linspace(0, 1, S)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")    # .cube order: R fastest
rgb = np.stack([r, gg, b], -1).reshape(-1, 3)


def luma(c):
    return c @ np.array([0.2126, 0.7152, 0.0722])


x = rgb.copy()
# contrast S-curve around 0.45
p = 0.45
x = np.where(x < p, p * (x / p) ** 1.25, 1 - (1 - p) * ((1 - x) / (1 - p)) ** 1.35)
# lift blacks / roll off whites
x = 0.025 + x * 0.955

Y = luma(x)[:, None]
sh = (1 - Y) ** 2.2
hi = Y ** 2.0
x = x + sh * np.array([-0.035, 0.015, 0.045]) + hi * np.array([0.06, 0.025, -0.045])

# vibrance
Y = luma(x)[:, None]
sat = x.max(1, keepdims=True) - x.min(1, keepdims=True)
amt = 0.35 * (1 - sat)
x = Y + (x - Y) * (1 + amt)

# emerald greens: where green dominates, pull a bit of red out, add blue
gdom = np.clip((x[:, 1:2] - np.maximum(x[:, 0:1], x[:, 2:3])) * 4, 0, 1)
x = x + gdom * np.array([-0.03, 0.01, 0.025])

x = np.clip(x, 0, 1)
with open("out/Bali_Golden_Hour.cube", "w") as f:
    f.write('TITLE "Bali Golden Hour"\nLUT_3D_SIZE 33\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
    for c in x:
        f.write(f"{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n")
print("Bali_Golden_Hour.cube written")

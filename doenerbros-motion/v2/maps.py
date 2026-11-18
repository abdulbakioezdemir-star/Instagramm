"""Heuristic depth + food masks for the product photos (no ML needed).
Food photos share one composition: dark steamy backdrop on top, wooden board + food centre/bottom."""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)

def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255

def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

for f in sys.argv[3:]:
    name = os.path.splitext(f)[0].split('-')[0]
    im = Image.open(os.path.join(src, f)).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    h, w = a.shape[:2]
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / (mx + 1e-4); val = mx
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    xx = np.ones((h, 1)) * np.linspace(0, 1, w)[None, :]
    # food saliency: bright & saturated, or very bright (sauce/bread highlights)
    sal = ss(.18, .5, sat * val) * ss(.25, .55, val) + ss(.75, .95, val) * .6
    sal *= ss(.12, .3, yy)                       # ignore steam at very top
    food = ss(.25, .6, blur(sal, 6))
    # close holes (dark meat / shadows inside the food): dilate then erode at 1/4 res
    small = Image.fromarray((food * 255).astype(np.uint8)).resize((w // 4, h // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(17)).filter(ImageFilter.MinFilter(9))
    closed = np.asarray(small.resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
    food = blur(np.maximum(food, closed * ss(.12, .3, yy)), 4)
    # depth: far backdrop top, table/board nearer toward bottom, food closest + rounded
    base = ss(.25, 1.0, yy) * .45
    centre = np.exp(-(((xx - .5) / .45) ** 2))
    dome = blur(food, 25) * .55 * (0.6 + 0.4 * centre)
    depth = np.maximum(base, base * .4 + dome + food * .2)
    depth = blur(depth, 6)
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-6)
    Image.fromarray((depth * 255).astype(np.uint8)).save(os.path.join(dst, name + '_depth.png'))
    Image.fromarray((np.clip(food, 0, 1) * 255).astype(np.uint8)).save(os.path.join(dst, name + '_mask.png'))
    print(name, w, h)

"""Removes the background of original.MOV with U2Net (rembg), smooths the matte edges,
and writes: ProRes 4444 with alpha, green-screen MP4, black MP4 and a PNG sequence."""
import glob
import os
import subprocess
import numpy as np
from PIL import Image
from rembg import new_session, remove

files = sorted(glob.glob("frames/*.png"))
sess = new_session("u2net")
alphas, rgbs = [], []
for f in files:
    im = Image.open(f).convert("RGB")
    a = np.asarray(remove(im, session=sess, only_mask=True), np.float32) / 255
    alphas.append(a)
    rgbs.append(np.asarray(im, np.float32) / 255)
import cv2
As = []
for a in alphas:
    # keep only the largest connected region (hand + arm), drop stray background bits
    m = (a > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate((lab == big).astype(np.uint8), np.ones((9, 9), np.uint8))
        a = a * keep
    # tighten + soften the edge a little (no halo)
    a = cv2.erode(a, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(a, (0, 0), 0.8)
    As.append(np.clip((a - 0.5) * 1.2 + 0.5, 0, 1))
os.makedirs("png_alpha", exist_ok=True)
for i, (rgb, a) in enumerate(zip(rgbs, As)):
    # de-spill: pull edge pixels slightly towards the hand interior colour (removes white fringe)
    edge = (a > 0.02) & (a < 0.9)
    rgb2 = rgb.copy()
    rgb2[edge] = rgb[edge] * 0.85
    out = np.dstack([rgb2, a])
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA").save(f"png_alpha/{i + 1:03d}.png")
print("frames", len(files))

common = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", "png_alpha/%03d.png", "-i", "original.MOV", "-map", "0:v", "-map", "1:a"]
subprocess.run(common + ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-c:a", "aac", "-shortest", "Hand_freigestellt_alpha.mov"], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=0x00FF00:s=480x360:r=30", "-framerate", "30", "-i", "png_alpha/%03d.png",
                "-i", "original.MOV", "-filter_complex", "[0][1]overlay=shortest=1[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "14",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "Hand_Greenscreen.mp4"], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=480x360:r=30", "-framerate", "30", "-i", "png_alpha/%03d.png",
                "-i", "original.MOV", "-filter_complex", "[0][1]overlay=shortest=1[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "14",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "Hand_Schwarz.mp4"], check=True)
print("done")

"""Kevin Nsimba 3D reel: beat-synced retime + energetic transitions, music only.
usage: python3 render_kevin_beat_sync.py VIDEO MUSIC OUT [WORKDIR]"""
import subprocess, sys, os
import numpy as np, soundfile as sf
VID, MUS, OUT = sys.argv[1:4]; W = sys.argv[4] if len(sys.argv) > 4 else "."
DUR = 16.4; BEAT = 0.5805

# ---- music bed: start on first hit (src 1.33), loop back into the drop so a 2nd drop lands on the logo
src = os.path.join(W, "src.wav"); bed = os.path.join(W, "bed.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MUS, "-vn", "-ac", "2", "-ar", "48000", src], check=True)
x, sr = sf.read(src)
seg = lambda a, b: x[int(a*sr):int(b*sr)]
A, B = seg(1.33, 15.30), seg(6.00, 9.5); n = int(.01*sr); w = np.linspace(0, 1, n)[:, None]
sf.write(bed, np.concatenate([A[:-n], A[-n:]*(1-w) + B[:n]*w, B[n:]]), sr)
DROP1, DROP2 = 4.67, 13.96                     # drops in bed time
beats = [round(DROP1 + k*BEAT, 3) for k in range(-8, 21) if 0 <= DROP1 + k*BEAT < DUR]
breaks = [(2.90, DROP1), (12.22, DROP2)]       # quiet build-ups in the song
in_break = lambda t: any(a <= t < b for a, b in breaks)

# ---- retime: (source video time -> output time), every visual change on a beat
A_MAP = [(0, 0), (0.75, 0.58), (1.95, 1.74), (2.85, 2.90), (4.65, DROP1), (5.87, 5.83), (6.25, 6.12),
         (6.95, 6.99), (7.58, 7.57), (8.50, 8.73), (9.10, 9.31), (9.78, 9.90), (10.45, 10.48),
         (11.12, 11.06), (12.05, 12.22), (13.20, DROP2), (16.4, DUR)]
expr = "0"
for (s0, o0), (s1, o1) in reversed(list(zip(A_MAP, A_MAP[1:]))):
    expr = f"if(lt(T,{s1}),{o0}+(T-{s0})*{(o1-o0)/(s1-s0):.5f},{expr})"

# ---- hits: (time, zoom punch, flash, shake, glitch)
cuts = {0.58: (.07, .25, 0, 1), 1.74: (.10, .45, .6, 1), 2.90: (.07, .3, 0, 1), DROP1: (.16, .7, 1, 1),
        5.83: (.10, 0, .5, 1), 6.12: (.05, 0, 0, 0), 6.99: (.09, 0, .4, 1), 7.57: (.08, 0, 0, 1),
        8.73: (.10, 0, .5, 1), 9.31: (.07, 0, 0, 1), 9.90: (.07, 0, 0, 1), 10.48: (.08, 0, .3, 1),
        11.06: (.09, 0, .4, 1), 12.22: (.06, 0, 0, 1), DROP2: (.14, 0, 1, 1)}
hits = dict(cuts)
for b in beats:                                 # small pulse on every other beat outside the breaks
    if not in_break(b) and all(abs(b - c) > .1 for c in cuts): hits[b] = (.03, 0, 0, 0)
e = lambda t0, tau: f"gte(t,{t0})*exp(-(t-{t0})/{tau})"
Z = "+".join(f"{z}*{e(t,.13)}" for t, (z, f, s, g) in hits.items())
# slow push-in through each break, released at the drop
Z += "".join(f"+0.07*between(t,{a},{b})*(t-{a})/({b}-{a})" for a, b in breaks)
F = "+".join(f"{f}*{e(t,.08)}" for t, (z, f, s, g) in hits.items() if f) or "0"
SH = "+".join(f"{s}*{e(t,.15)}" for t, (z, f, s, g) in hits.items() if s) or "0"
G = "+".join(f"between(t,{t}-0.02,{t}+0.12)" for t, (z, f, s, g) in hits.items() if g)

vf = (f"[0:v]setpts='({expr})/TB',fps=30,"
      f"scale=w='2*trunc(1145*(1+{Z})/2)':h='2*trunc(2036*(1+{Z})/2)':eval=frame,"
      f"crop=1080:1920:x='(iw-1080)/2+30*({SH})*sin(t*97)':y='(ih-1920)/2+24*({SH})*cos(t*83)',"
      f"eq=brightness='0.85*({F})':eval=frame,split[base][fx];"
      f"[fx]tmix=frames=3,rgbashift=rh=-18:bh=18:rv=4:bv=-4:edge=smear[gl];"
      f"[base][gl]overlay=enable='{G}',trim=0:{DUR},setpts=PTS-STARTPTS,format=yuv420p[v]")
af = (f"[1:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,afade=t=out:st={DUR-0.45}:d=0.45,"
      "loudnorm=I=-13:TP=-1:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VID, "-i", bed, "-filter_complex", vf + ";" + af,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-t", str(DUR),
                "-movflags", "+faststart", OUT], check=True)

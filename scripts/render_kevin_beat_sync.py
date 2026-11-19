"""Kevin Nsimba 3D reel: beat-synced retime + energetic transitions, music only.
usage: python3 render_kevin_beat_sync.py VIDEO MUSIC OUT [WORKDIR]"""
import subprocess, sys, os
import numpy as np, soundfile as sf
VID, MUS, OUT = sys.argv[1:4]; W = sys.argv[4] if len(sys.argv) > 4 else "."
DUR = 16.4

# ---- music bed: start on first hit (src 1.33), loop back into the drop so a 2nd drop lands on the logo
src = os.path.join(W, "src.wav"); bed = os.path.join(W, "bed.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MUS, "-vn", "-ac", "2", "-ar", "48000", src], check=True)
x, sr = sf.read(src)
seg = lambda a, b: x[int(a*sr):int(b*sr)]
A, B = seg(1.33, 15.30), seg(6.00, 9.5); n = int(.01*sr); w = np.linspace(0, 1, n)[:, None]
sf.write(bed, np.concatenate([A[:-n], A[-n:]*(1-w) + B[:n]*w, B[n:]]), sr)
DROP1, DROP2 = 4.69, 13.98                     # drops in bed time (measured kicks)
breaks = [(3.02, DROP1), (12.14, DROP2)]       # quiet build-ups in the song

# ---- retime: (source video time -> output time); every visual change lands on a measured kick/clap
A_MAP = [(0, 0), (0.75, 0.91), (1.95, 2.03), (2.85, 3.02), (4.65, DROP1), (5.87, 5.81), (6.25, 6.44),
         (6.95, 7.31), (7.58, 7.89), (8.50, 8.77), (9.10, 9.34), (9.78, 10.22), (10.45, 11.09),
         (11.12, 12.14), (12.05, 12.83), (13.20, DROP2), (16.4, DUR)]
expr = "0"
for (s0, o0), (s1, o1) in reversed(list(zip(A_MAP, A_MAP[1:]))):
    expr = f"if(lt(T,{s1}),{o0}+(T-{s0})*{(o1-o0)/(s1-s0):.5f},{expr})"

# ---- hits: (time, zoom punch, flash, soft motion blur) -- no shake, text parts kept gentle
hits = {0.91: (.04, 0, 1), 2.03: (.05, 0, 1), 3.02: (.04, 0, 1), DROP1: (.08, .35, 1),
        5.81: (.03, 0, 0), 6.44: (.02, 0, 0), 7.31: (.025, 0, 0), 7.89: (.02, 0, 0),
        8.77: (.03, 0, 0), 9.34: (.02, 0, 0), 10.22: (.02, 0, 0), 11.09: (.025, 0, 0),
        12.14: (.02, 0, 0), 12.83: (.02, 0, 0), DROP2: (.05, .2, 0)}
e = lambda t0, tau: f"gte(t,{t0})*exp(-(t-{t0})/{tau})"
Z = "+".join(f"{z}*{e(t,.18)}" for t, (z, f, b) in hits.items())
Z += "".join(f"+0.04*between(t,{a},{b})*(t-{a})/({b}-{a})" for a, b in breaks)   # gentle push-in
F = "+".join(f"{f}*{e(t,.10)}" for t, (z, f, b) in hits.items() if f)
G = "+".join(f"between(t,{t}-0.03,{t}+0.07)" for t, (z, f, b) in hits.items() if b)

vf = (f"[0:v]setpts='({expr})/TB',fps=30,"
      f"scale=w='2*trunc(1080*(1+{Z})/2)':h='2*trunc(1920*(1+{Z})/2)':eval=frame,"
      f"crop=1080:1920,"
      f"eq=brightness='0.8*({F})':eval=frame,split[base][fx];"
      f"[fx]tmix=frames=3[gl];"
      f"[base][gl]overlay=enable='{G}',trim=0:{DUR},setpts=PTS-STARTPTS,format=yuv420p[v]")
af = (f"[1:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,afade=t=out:st={DUR-0.45}:d=0.45,"
      "loudnorm=I=-13:TP=-1:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VID, "-i", bed, "-filter_complex", vf + ";" + af,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-t", str(DUR),
                "-movflags", "+faststart", OUT], check=True)

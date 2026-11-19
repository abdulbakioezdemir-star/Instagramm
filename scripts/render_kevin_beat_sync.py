import subprocess, sys
U="/root/.claude/uploads/b2719d54-f67c-57f5-8095-61cad9732262/"
VID=U+"d69a024f-kevin-nsimba-3d.mp4"; MUS=U+"ae7c1c80-Musik.MP4"
OUT=sys.argv[1]
# (source time -> output time): transitions land on music beats (output grid ~ 1.29 + k*0.5805)
A=[(0,0),(1.95,2.16),(2.85,3.03),(4.65,4.78),(5.87,5.96),(6.25,6.25),(6.95,7.10),(7.58,7.70),
   (8.50,8.86),(9.10,9.44),(9.78,10.02),(10.45,10.60),(11.12,11.47),(12.05,12.35),(16.4,16.4)]
# piecewise-linear setpts expression on input time T
expr="0"
for (s0,o0),(s1,o1) in reversed(list(zip(A,A[1:]))):
    k=(o1-o0)/(s1-s0)
    expr=f"if(lt(T,{s1}),{o0}+(T-{s0})*{k:.5f},{expr})"
# effects at output beat times: (time, zoom amount, flash, shake)
FX=[(1.29,.04,0,0),(2.16,.08,.35,0),(3.03,.06,0,0),(4.78,.08,.45,0),(5.96,.12,.6,1),
    (6.25,.04,0,0),(7.10,.07,.25,0),(7.70,.06,0,0),(8.86,.09,.45,0),(9.44,.05,0,0),
    (10.02,.05,0,0),(10.60,.06,.2,0),(11.47,.07,0,0),(12.35,.06,.4,0)]
def env(t0,tau): return f"gte(t,{t0})*exp(-(t-{t0})/{tau})"
Z="1+"+"+".join(f"{a}*{env(t,0.14)}" for t,a,f,s in FX)
F="+".join(f"{f}*{env(t,0.09)}" for t,a,f,s in FX if f) 
SH="+".join(f"{env(t,0.12)}" for t,a,f,s in FX if s)
vf=(f"setpts='({expr})/TB',fps=30,"
    f"scale=w='2*trunc(1145*({Z})/2)':h='2*trunc(2036*({Z})/2)':eval=frame:flags=bicubic,"
    f"crop=1080:1920:x='(iw-1080)/2+28*({SH})*sin(t*95)':y='(ih-1920)/2+22*({SH})*cos(t*83)',"
    f"eq=brightness='0.9*({F})':eval=frame,"
    f"trim=0:16.4,setpts=PTS-STARTPTS,format=yuv420p")
# music: output = musicsrc - 0.1, muted until first beat at 1.27, fade out over the end break
af=("atrim=0:16.4,asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,1.27),0,1)':eval=frame,"
    "afade=t=in:st=1.27:d=0.03,afade=t=out:st=13.9:d=1.2,loudnorm=I=-14:TP=-1:LRA=11,apad")
cmd=["ffmpeg","-v","error","-y","-i",VID,"-ss","0.1","-i",MUS,
     "-filter_complex",f"[0:v]{vf}[v];[1:a]{af}[a]","-map","[v]","-map","[a]",
     "-c:v","libx264","-preset","slow","-crf","17","-profile:v","high","-pix_fmt","yuv420p",
     "-c:a","aac","-b:a","256k","-t","16.4","-movflags","+faststart",OUT]
subprocess.run(cmd,check=True)

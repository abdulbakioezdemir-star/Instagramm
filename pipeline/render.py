import sys, subprocess, os, skia
import scenes as S
import json
SCENES=json.load(open('/home/claude/timeline.json'))['scenes']
FPS=30
def render(idx):
    name,a,b=SCENES[idx]
    f0,f1=round(a*FPS),round(b*FPS)
    tmp=f"/home/claude/out/s{idx}_{name}.tmp.mp4"; fin=tmp.replace('.tmp','')
    p=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","bgra","-s","1080x1920","-r","30","-i","-",
        "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-r","30",tmp],stdin=subprocess.PIPE)
    s=skia.Surface(1080,1920); c=s.getCanvas()
    for f in range(f0,f1):
        c.save(); S.frame(c,name,f/FPS); c.restore()
        p.stdin.write(s.makeImageSnapshot().tobytes())
    p.stdin.close()
    if p.wait()==0: os.replace(tmp,fin); print("ok",fin,flush=True)
if __name__=="__main__":
    for i in sys.argv[1:]: render(int(i))

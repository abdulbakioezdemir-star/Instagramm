import sys, skia
from PIL import Image
import scenes as S
import json
SCENES=json.load(open('/home/claude/timeline.json'))['scenes']
def scene_at(t):
    for n,a,b in SCENES:
        if a<=t<b: return n
    return SCENES[-1][0]
ts=[float(x) for x in sys.argv[2:]]
ims=[]
for t in ts:
    s=skia.Surface(1080,1920); c=s.getCanvas()
    S.frame(c,scene_at(t),t)
    im=Image.frombytes('RGBA',(1080,1920),s.makeImageSnapshot().tobytes(),'raw','BGRA').convert('RGB')
    ims.append(im.resize((360,640)))
cols=min(4,len(ims)); rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(360*cols,640*rows),'black')
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*360,(i//cols)*640))
sheet.save(sys.argv[1])

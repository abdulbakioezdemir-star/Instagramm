from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
F="/home/claude/instagramm/pipeline/fonts/Bungee-Regular.ttf"
def emblem(S=1080, bg=(12,30,52)):
    img=Image.new("RGB",(S,S),bg); d=ImageDraw.Draw(img)
    c=S/2; R=S*0.40
    gold=(240,190,80); navy=(14,42,71)
    d.ellipse([c-R-18,c-R-18,c+R+18,c+R+18],fill=gold)
    d.ellipse([c-R,c-R,c+R,c+R],fill=navy)
    # inner scene clipped to circle
    sc=Image.new("RGB",(S,S)); sd=ImageDraw.Draw(sc)
    for y in range(S):
        t=y/S; sd.line([(0,y),(S,y)],fill=(int(255-90*t),int(180-60*t),int(100+30*t)))
    sd.ellipse([c-90,c-250,c+90,c-70],fill=(255,226,120))
    sd.polygon([(c-R,c+120),(c-170,c-170),(c-20,c+40),(c+120,c-120),(c+R,c+120)],fill=(40,70,84))
    sd.polygon([(c-170,c-170),(c-215,c-95),(c-175,c-112),(c-135,c-90),(c-120,c-115)],fill=(245,248,252))
    sd.polygon([(c+120,c-120),(c+80,c-55),(c+120,c-70),(c+160,c-48),(c+175,c-70)],fill=(245,248,252))
    sd.rectangle([0,c+110,S,S],fill=(18,96,160))
    for i,y in enumerate(range(int(c+125),int(c+R),42)):
        for x in range(-40+(i%2)*45,S,90): sd.arc([x,y,x+90,y+36],200,340,fill=(150,210,240),width=8)
    m=Image.new("L",(S,S),0); ImageDraw.Draw(m).ellipse([c-R+14,c-R+14,c+R-14,c+R-14],fill=255)
    img.paste(sc,(0,0),m)
    # banner
    f=ImageFont.truetype(F,int(S*0.105))
    t="VALMORA"; w=d.textlength(t,font=f); h=int(S*0.15)
    by=c+R*0.47
    d.rounded_rectangle([c-w/2-50,by,c+w/2+50,by+h],radius=24,fill=gold)
    d.text((c-w/2,by+h*0.13),t,font=f,fill=navy)
    f2=ImageFont.truetype(F,int(S*0.035))
    t2="EST. 2026"; w2=d.textlength(t2,font=f2)
    d.text((c-w2/2,c-R*0.82),t2,font=f2,fill=navy)
    return img
emblem().save("logo_valmora.jpg",quality=94)
emblem(bg=(240,190,80)).save("profilbild_valmora.jpg",quality=94)

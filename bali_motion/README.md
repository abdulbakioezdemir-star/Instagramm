# Bali Motion Edit

16 s · 1080x1920 (Reel/TikTok) · 30 fps · 120 BPM · ohne Stimme

- `out/Bali_Motion_Edit.mp4`: fertiges Video (gegradet, mit Sound)
- `out/Bali_Golden_Hour.cube`: CC-Filter / LUT (Premiere, DaVinci, CapCut, AE, ffmpeg)
- `out/soundtrack.wav`: Musik + Sound Design einzeln
- `out/vorher_nachher_cc.jpg`: Vergleich ohne/mit Color Grading

Neu erzeugen:
```
pip install numpy pillow opencv-python-headless
python3 audio.py && python3 make_lut.py && python3 render.py out/bali_raw.mp4
ffmpeg -i out/bali_raw.mp4 -i out/soundtrack.wav -vf "lut3d=out/Bali_Golden_Hour.cube,eq=saturation=1.08,unsharp=5:5:0.4,vignette=angle=PI/5,noise=alls=4:allf=t+u" -c:v libx264 -crf 19 -c:a aac -b:a 256k -shortest out/Bali_Motion_Edit.mp4
```

## Timeline (1 Beat = 15 Frames)
| Zeit | Szene | Übergang / Effekt | Sound |
|---|---|---|---|
| 0–4 s | Sonnenuntergang am Meer, Tanah Lot | 3D-Titel „BALI“ fliegt ein, Slam auf Beat 3 | Meeresrauschen, Gamelan, Gong + Impact |
| 4 s | → Reisterrassen Ubud | Whip Pan mit Motion Blur | Whoosh |
| 6 s | → Tempeltor „Gates of Heaven“ | 3D-Flip, Dolly-Push-in, Shake + RGB-Split steigern sich | Riser + Snare-Roll |
| 7,87 s | 4 Frames Schwarz | Spannungsmoment vor dem Drop | Stille |
| 8–12 s | DROP: Schnitt auf jedem Beat, dann jedem halben Beat | Zoom Burst, Flash, RGB-Split, 3D-Wörter | Sub-Impact, Whoosh + Tick pro Schnitt |
| 12–14 s | Palmen-Parallax (3 Tiefenebenen) | Zoom Burst rein und raus | Breakdown |
| 14–16 s | Finale am Tor, 3D-Titel | Zoom Burst, Fade | Gong, Ausklang |

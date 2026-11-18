# DönER Bro's – 3D Motion Video

22-Sekunden-Video im Format 9:16 (1080×1920, 30 fps) mit Sound mit einer durchgehenden Kamerafahrt durch eine 3D-Szene in Three.js:

| Zeit | Szene |
|---|---|
| 0–3 s | Intro: Neon-Ring zeichnet sich, Wortmarke „DönER Bro's“, die Kamera fliegt durch den Ring |
| 3–7 s | Döner-Spieß dreht sich vor dem glühenden Grill, mit Neon-Spirale und Glut: „Hausgemachtes Dönerfleisch.“ |
| 7–10.5 s | Der Döner im Brot füllt sich (Fleisch, Salat, Tomate, Zwiebel, Sauce fallen hinein): „Frisch. Saftig. Legendär.“ · ab 7,00 € |
| 10.5–14.5 s | Der Chicken Burger stapelt sich Schicht für Schicht, kurze Explosionsansicht |
| 14.5–17.5 s | Pizza, die Beläge fallen auf den Teig: „Pizza-Montag · Jede Pizza 8,00 €“ |
| 17.5–22 s | Outro: Logo landet mittig, dann zieht sich der Neon-Ring darum (Impact), danach Adresse, Nummer, halal, Öffnungszeiten |

Alle Speisen sind prozedural modelliert, es gibt keine externen 3D-Modelle. Das Logo stammt von doenerbros-kolbermoor.de.

## Neu rendern

```bash
node render.js video DoenerBros_Motion_3D.mp4 30   # komplettes Video (benötigt playwright + ffmpeg)
OUT=. node render.js stills 2,5,9,12                 # einzelne Standbilder zur Kontrolle
```

Texte, Preise und Zeiten stehen als HTML in `scene.html` oben. Die Kamerafahrt ist im Array `camKeys` festgelegt (ein Keyframe pro Sekunde).

## Sound

`sound.py` erzeugt Musik und Effekte synthetisch: einen Beat mit 120 BPM, eine orientalische Saz-Melodie, Whooshes an jedem Übergang, Brutzeln am Spieß, Plops, Burger-Schläge und einen Impact beim Ring. Alles ist lizenzfrei.

```bash
python3 sound.py soundtrack.wav
ffmpeg -i video.mp4 -i soundtrack.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k out.mp4
```

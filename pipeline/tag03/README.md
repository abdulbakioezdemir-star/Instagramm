# Tag 3 „Kamera kaputt“ – Teil 1 (12 Uhr) & Teil 2 (18 Uhr)

Abstimmung Tag 2 Teil 2: **B 7 : A 0** → Ahmed sagt Lena, seine Kamera sei kaputt.
- Teil 1 (gepostet 2026-11-11 12:00, 31,7 s): Cold Open „Ich hab Lena gesagt, meine Kamera ist kaputt. Sie war an.“ (+ Text „MEINE KAMERA WAR AN.“ ab 0 s)
  → Rückspul „1 MINUTE VORHER“ → 7:0-Karte („Ihr wollt mein Gesicht also genauso wenig sehen wie ich“) → Videoanruf, Daumen hoch „Alles schwarz. Voll schade.“
  → harter Schnitt Front-Kamera von unten: Lena „…eigentlich nur deine Nasenlöcher“ (Stempel HD-NASENLÖCHER) → „Sie hat mich gesehen … Was jetzt?!“ + „TEIL 2 · HEUTE 18 UHR“.
- Teil 2 (18 Uhr, fertig getestet, 30,4 s): „VORHIN BEI AHMED…“ Nasenloch-Cam → „Das ist ein Filter!“ (Pill FILTER: PLEITE & KALT) → Lena „Ein Filter… der zittert?“
  → „Der Filter heißt: Pleite und kalt.“ → Lena „Du bist süß, wenn du lügst. Aber wer bist du wirklich?“ (ERWISCHT) → Poll A = Die Wahrheit sagen, B = „Ich bin Emres Zwilling“ → „TAG 4 – MORGEN 12 UHR“.

## Rendern (18-Uhr-Lauf)
Setup wie in `pipeline/tag02/README.md` (pip edge-tts skia-python, draw.py/scenes.py/audio.py/mix.sh/tts.py/fonts nach /home/claude, Dummy-timeline.json, /home/claude/tag2).
Repo muss unter `/home/claude/instagramm` liegen (Branch content).
```bash
cd /home/claude/instagramm/pipeline/tag03
python3 tag03.py 2 tts
python3 tag03.py 2 preview 0.5 4 7 10 13 16 19 22 25 28   # -> /home/claude/tag03_work/teil2/prev.png
python3 tag03.py 2 all /home/claude/instagramm/media/glowup/tag03_teil2.mp4
```
Caption-Vorschlag Teil 2:
Tag 3 · Teil 2/2 / Lena sieht nur Ahmeds Nasenlöcher – und er sagt, das ist ein Filter. Filtername: „Pleite & kalt“ 🥶 /
A = Die Wahrheit sagen / B = „Ich bin Emres Zwilling“ / Schreibt A oder B – die Mehrheit entscheidet Tag 4 (morgen 12 Uhr)! / #ahmedglowup #animation #comedy #dating #reels

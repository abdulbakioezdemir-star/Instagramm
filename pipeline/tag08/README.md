# Tag 8 „Lena zu Mama“ – ein Reel (12 Uhr, BEFEHLE.md Befehl 5)

Abstimmung Tag 7: **A 4 : B 0** → Lena kommt Sonntag zu Mama.
Ablauf (~32,0 s): Hook „Ich hab Lena zu meiner Mama eingeladen. Wir hatten noch kein Date.“ (Text „ERSTES DATE: BEI MAMA.“, Stempel 0 DATES)
→ Chat: 20 Minuten getippt, geschickt „Sonntag Hunger?“ → Lena „Wer kocht?“ – „Meine Mama.“ → „Erst Mama, dann du? Okay, ich komme.“ (SIE KOMMT!)
→ Familiengruppe (47): „Ich sag Bekannte. Mama schreibt der Familie: Verlobte.“ (VERLOBTE?!, Tante Fatma „Aus guter Familie?“, Onkel bringt den Grill, Oma fragt nach Hochzeit)
→ Lena „Endlich sehe ich dich in echt!“ → Tinder-Karte (Emre) VS Ahmed echt: „Mit meinem Gesicht. Nicht Emres.“ (SONNTAG: ECHTES GESICHT)
→ Poll A = Emre mitnehmen, B = Friseur: wie Emre → „FOLG MIR · TAG 9 MORGEN 12 UHR“.

## Rendern
Setup wie `pipeline/tag02/README.md` (inkl. TTS-Schleife für /home/claude/tag2). Neu: `scissors()`, Szene `gruppe`, `echt`.
```bash
python3 tag08.py 1 tts
python3 tag08.py 1 preview 0.3 2.8 5 9 13.5 18.5 22.5 24.5 27 31.5
python3 tag08.py 1 all <repo>/media/glowup/tag08.mp4
```

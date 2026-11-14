# Tag 5 „Ahmed spielt beide“ – ein Reel (12 Uhr, BEFEHLE.md Befehl 5)

Abstimmung Tag 4 Teil 2: **B 3 : A 0** → Ahmed spielt Emre und sich selbst.
Ablauf (32,0 s): Hook „Ich hab vor Lena meinen eigenen Zwilling gespielt. Live.“ (Text „ICH BIN JETZT MEIN ZWILLING.“, Stempel LIVE)
→ „Cappy auf: Emre. Cappy ab: Ahmed. 100 % sicher.“ → Lena „Emre, warum klingst du genau wie Ahmed?“ → „Wir teilen uns eine Stimme. Ist billiger.“ (SPARTARIF)
→ Lena „Okay. Dann seh ich euch morgen. Beide. Gleichzeitig.“ (GLEICHZEITIG?!) → Poll A = Emre mit Döner bestechen, B = Die Wahrheit sagen → „FOLG MIR · TAG 6 MORGEN 12 UHR“.

## Rendern
Setup wie `pipeline/tag04/README.md` (inkl. TTS-Schleife für /home/claude/tag2). Neu: Stille am Zeilenende wird gekappt (Tempo).
```bash
cd /home/claude/instagramm/pipeline/tag05
python3 tag05.py 1 tts
python3 tag05.py 1 preview 0.4 2 5 9 14 20 23 27 31
python3 tag05.py 1 all /home/claude/instagramm/media/glowup/tag05.mp4
```

# Tag 7 „Mama um Geld fragen“ – ein Reel (12 Uhr, BEFEHLE.md Befehl 5)

Abstimmung Tag 6: **A 3 : B 1** → Ahmed fragt Mama um Geld.
Ablauf (~32,1 s): Hook „Ich hab Mama um Geld für einen Döner gefragt. Ich bin siebenundzwanzig.“ (Text „ICH BIN 27. ICH FRAG MAMA.“, Stempel 27 JAHRE ALT)
→ Chat „Mama, leihst du mir 15 Euro? Für Bildung.“ → 4-Minuten-Sprachnachricht („Bei Minute 3 war sie noch bei meiner Geburt.“)
→ „WER IST DAS MÄDCHEN?“ → Tante Fatma hat Tinder gesehen – mit Emres Gesicht (FALSCHES GESICHT)
→ Überweisung +15 € „Verwendungszweck: Sonntag bringst du sie mit.“ (SONNTAG. ESSEN.)
→ Poll A = Lena mitbringen, B = Es gibt kein Mädchen → „FOLG MIR · TAG 8 MORGEN 12 UHR“.

## Rendern
Setup wie `pipeline/tag04/README.md`. Neue Helfer: `mama_icon(..., scarf, glasses)`, `voice_note()`.
```bash
python3 tag07.py 1 tts
python3 tag07.py 1 preview 0.3 2.5 4.6 8 10.5 13 15.5 17.5 19.8 23.5 27 31.5
python3 tag07.py 1 all <repo>/media/glowup/tag07.mp4
```

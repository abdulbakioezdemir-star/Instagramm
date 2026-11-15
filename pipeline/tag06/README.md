# Tag 6 „Emre mit Döner bestechen“ – ein Reel (12 Uhr, BEFEHLE.md Befehl 5)

Abstimmung Tag 5: **A 5 : B 0** → Ahmed besticht Emre mit Döner.
Ablauf (~31,9 s): Hook „Ich wollte meinen Cousin mit einem Döner bestechen. Ich hatte drei Euro vierzig.“ (Text „ICH BESTECHE MEINEN COUSIN.“, Stempel 3,40 €)
→ Dönermann „Döner: 8,50 €“ → „Und ohne Fleisch, ohne Brot?“ → „Dann ist es eine Serviette.“ (SERVIETTE: 3,40 €)
→ Chat: Emre antwortet seit 3 Wochen nur mit Daumen hoch → „Döner geht auf mich“ → „BIN DA“ in 0,8 s + „extra Fleisch, Pommes, Ayran“
→ „Ich hab immer noch drei Euro vierzig.“ → Poll A = Mama um Geld fragen, B = Döner auf Raten → „FOLG MIR · TAG 7 MORGEN 12 UHR“.

## Rendern
Setup wie `pipeline/tag04/README.md`. Dönermann-Figur `chef()` jetzt in tag06.py; `wf(zeile, wort)` findet Wort-Zeitpunkte per Text.
```bash
python3 tag06.py 1 tts
python3 tag06.py 1 preview 0.4 2.5 4.6 6.5 9 11.3 13 15.5 18 20.5 23.5 26 28.5 31.5
python3 tag06.py 1 all <repo>/media/glowup/tag06.mp4
```

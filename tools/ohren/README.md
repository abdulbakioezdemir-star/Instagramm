# Ohren für Claude

Claude kann Ton nicht direkt hören. Diese zwei Werkzeuge kommen dem nahe:

- `hoeren.py <datei> [modell]` – schreibt gesprochene Sprache mit Whisper ab (Deutsch). Damit prüft man, ob eine Stimme verständlich ist und das Richtige sagt. Einmalig nötig: `pip install faster-whisper` (das Modell „small" wird beim ersten Start heruntergeladen).
- `spektrum.sh <datei> [ordner]` – zeichnet Spektrogramm und Wellenform als Bild. Darauf sieht man Musik, Stimme, Schläge, Lücken und zu laute Stellen.

Nicht erkennbar sind damit Geschmacksfragen wie „klingt die Stimme sympathisch" oder „passt die Musik zur Stimmung".

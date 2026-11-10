# Valmora – Learnings

## Zahlen
| Reel | gepostet | Views | Likes | Kommentare | Shares | Skip-Rate | Ø Watch-Time | Follower |
|---|---|---|---|---|---|---|---|---|
| Tag 1 (Gründung, 45 s) | 2026-11-09 23:29 | 115 | 1 | 0 | 0 | 52,8 % | 6,9 s | 1 |
| Tag 2 · Teil 1 (Bootssteg, 49 s) | 2026-11-10 15:01 | – | – | – | – | – | – | – |

## Tag 1 → Tag 2 (2026-11-10)
- Schlecht: Mehr als die Hälfte wischt in den ersten 3 s weg, Ø nur ~7 s von 45 s. Kein einziger Kommentar → Mitmach-Mechanik greift noch nicht.
- Posting um 23:29 war spät – kaum Reichweite in der Nacht.
- Geändert in Tag 2: Text ab Frame 0 (kein Schwarz-Fade-in), sofort Konflikt im Hook („nur noch 200 €“ in rotem Kasten), Taiko-Schlag auf 0,05 s,
  Spannung „fast pleite – ich brauche euch“ statt neutraler Erklärung. Kürzere Pausen zwischen Sätzen (0,35 s statt 0,6 s).
- Technik: Untertitel-Gruppen brechen jetzt nach Breite um (lange Zahlwörter wie „ZWEIHUNDERTEINS“ wurden abgeschnitten). Bauten in bauten.py ausgelagert.
- edge-tts muss in neuer Umgebung installiert werden (`pip install edge-tts --break-system-packages`).

## Nächstes Mal
- Tag-2-Zahlen (Skip-Rate!) mit Tag 1 vergleichen. Wenn Skip-Rate weiter > 45 %: Hook noch kürzer (≤ 2 s gesprochen), erstes Bild = fertiger Bau/Boot in Bewegung.
- Wenn wieder keine Kommentare: konkrete A/B-Frage stellen („Schule oder Bäckerei?“) – leichter zu beantworten als offene Frage.
- Zahlen in der Erzählung kurz halten (lange Zahlwörter bremsen).

## 2026-11-10 Analyse (Chat mit Besitzer, 17:30)
- Tag 1 (55 s): 125 Views, Skip 53 %, Ø nur 6,9 s Watch-Time → zu lang, die meisten gehen nach dem Intro.
- Tag 2 (kürzer): 343 Views, 11 Likes, 1 Kommentar, Skip 39 % → deutlich besser. Kürzer und direkter funktioniert.
- Problem: Offene Frage „Was bauen wir?“ bringt kaum Kommentare. Bei Ahmed bringt A/B 8 Kommentare.
- **Ab sofort:** Jedes Bau-Reel (Teil 1/2, Teil 2/2) endet mit **3 nummerierten Optionen** groß im Bild
  („1 = Hafen · 2 = Bäckerei · 3 = Brücke – schreib die Zahl!“), gleiche Optionen in der Caption.
  Eigene Wünsche bleiben erlaubt; der Top-Kommentar gewinnt, sonst die meistgenannte Zahl.
- Erste Sekunde: sofort das Land + große Zahl (Kasse oder Einwohner) zeigen, kein langsames Intro.

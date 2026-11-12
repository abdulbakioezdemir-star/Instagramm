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

## 2026-11-10 21:00 – Tag 2 · Teil 2/2 (Bäckerei, 32 s)
- Zahlen vor dem Post: Tag 1 131 Views / 1 Like / Skip 53,7 % / Ø 7,2 s. Tag 2·T1 598 Views / 15 Likes / 1 Kommentar / Skip 55,4 % / Ø 9,7 s. Follower 7.
- Erster echter Top-Kommentar: „Bau einen Bäcker“ (1 Like; Username über API leer → im Video „Top-Kommentar“ statt Name). Umgesetzt, Antwort unter den Kommentar gesetzt.
- Länge nach Befehl 2: 32 s (6 Sätze statt 8). Test des Tages: **Hook-Art „Konsequenz zuerst“** – 3 Varianten: (A) „Ihr wolltet einen Bäcker. Ich habe sechs Euro übrig.“ (B) „Mein Land hat jetzt Brot. Aber kein Geld mehr.“ (C) „Ein einziger Kommentar hat gerade fast mein ganzes Geld ausgegeben.“ → **C gewählt** (Neugier + Mitmach-Hinweis). Fliegende Münzen ab Frame 0 für Bewegung, roter Kasten „66 € → 6 €“.
- Selbstironie-Zeile (Befehl 3): „Das Brot ist frisch. Der Gründer ist pleite.“ als zwei Karten (grün/rot).
- Ende mit 3 nummerierten Optionen (1 Fischerhütte · 2 Brunnen · 3 Garten) im Bild + Caption.
- Technik: tts.py neu (edge-tts braucht in der Cloud den Proxy-CA `/root/.ccr/ca-bundle.crt`, sonst SSL-Fehler; tts.py setzt das automatisch). Bäckerei-Schild auf die Wand statt aufs Dach (sonst abgeschnitten).
- Nächstes Mal prüfen: Skip-Rate von Teil 2 vs. Teil 1 (55 %) → zeigt, ob der Konsequenz-Hook besser hält. Kasse ist fast leer → Spannung „reicht das Geld?“ nutzen.

## 2026-11-11 15:00 – Tag 3 · Teil 1/2 (Fischerhütte, 32 s)
- Zahlen vor dem Post (≈ 17–24 h): Tag 1 145 Views / 2 Likes / Skip 53,5 % / Ø 9,2 s. Tag 2·T1 1.175 Views / 32 Likes / 3 Kom. / Skip 52,1 % / Ø 9,6 s.
  **Tag 2·T2 (Bäckerei, Konsequenz-Hook)** 541 Views / 20 Likes / **8 Kommentare** / **Skip 39 %** / Ø 11,9 s. Follower 12 (gestern 7). Shares überall 0.
- Ergebnis Test gestern: Konsequenz-Hook + 3 nummerierte Optionen → Skip-Rate 52 % → 39 %, Kommentare 3 → 8. **Gewinner, beibehalten.**
- Kommentare unter T2: 3× „1“ (korosensei0815, eliasbike2026, karstenffm), 1× „3“, „Bau eine Strandbar“ (till.ue), „mach mich zum Bäckerei-Chef“ (tizianspahn). Alle 0 Likes → meistgenannte Zahl gewinnt: Fischerhütte (−40 €). Bonus: tizianspahn wird Bäckerei-Chef (kostenlos, „Gehalt: 1 Brötchen“ = Selbstironie-Zeile).
- Kasse: 1000 + 54 Likes − 1010 = 44 € → nach Hütte 4 €.
- **Test des Tages: Namen der Abstimmenden im Bild** (3 Usernames groß in der Stats-Szene + Bäckerei-Chef-Ernennung). Hypothese: Wer seinen Namen sieht, kommentiert wieder/teilt (Shares bisher 0). Hook-Varianten: (A) „Drei von euch haben die Eins gewählt. Ich habe 44 €.“ (B) „Ich hab einen Bäckerei-Chef ernannt. Gehalt: ein Brötchen.“ (C) „Mein Land hat nur noch 44 Euro – und ihr wollt eine Fischerhütte.“ → **A gewählt** (Mitmach-Beweis + Geldspannung, kurz).
- Neue Optionen: 1 Strandbar (Zuschauerwunsch till.ue) · 2 Brunnen · 3 Garten.
- Technik: tag03.py nutzt relative Font-Pfade (läuft in jedem Clone-Ordner). Fischerhütte in bauten.py (x=590, Boden 1885, unterhalb der Untertitel). Bauphase nur 1,4 s → nächstes Mal Bau länger zeigen (eigener Satz).
- Nächstes Mal: Shares-Zahl von Tag 3 prüfen; wenn Namen im Bild Kommentare steigern → fest übernehmen. Kasse ~4 € → Strandbar braucht Likes: „Wenn ihr X Likes schafft, baue ich…“ als Ziel-Mechanik testen.
- Gepostet 15:00 Berlin, media_id 18118625588112500. 7 Kommentare beantwortet (Abstimmende, Strandbar-Wunsch, Bäckerei-Chef, 'Wo ist die Mauer?'). Keine Spam-Kommentare.

## 2026-11-11 21:00 – Tag 3 · Teil 2/2 (Strandbar, 32 s)
- Zahlen vor dem Post: Tag 1 149 Views / 2 Likes / Skip 54 %. Tag 2·T1 1.194 / 33 / 4 Kom. / Skip 52 % / Ø 9,7 s. Tag 2·T2 (Bäckerei) 751 / 25 / 14 Kom. / **Skip 37 %** / Ø 12,0 s. Tag 3·T1 (Fischerhütte, ~5,5 h alt) 195 / 5 / 3 Kom. / Skip 41 % / Ø 8,4 s. Follower 14 (+2). Shares weiterhin überall 0.
- Tag 3·T1 läuft nach 5 h deutlich schwächer als T2 gestern (195 vs. 541 Views zum ähnlichen Zeitpunkt) – Namen-im-Bild-Test noch nicht auswertbar; 3 Kommentare, alle „1“ (Strandbar).
- Abstimmung: 3× „1“ (587pii, till.ue, 041_sxcz_; alle 0 Likes) → Strandbar (Wunsch von till.ue). Kasse 1000 + 65 − 1050 = 15 € → Strandbar −15 € → **0 €**.
- **Test des Tages: Like-Ziel-Mechanik** – Kasse ist leer, Reel betont „1 Like = 1 €“ groß in der Abstimmungsszene. Hypothese: mehr Likes pro View als bisher (Ø ~3 %). Auswerten: Likes/Views von T2 vs. T1.
- Hook-Varianten: (A) „Drei Stimmen für die Strandbar. Danach hatte mein Land null Euro.“ (B) „Meine Strandbar ist offen. Ich kann mir kein Getränk leisten.“ (C) „Fünfzehn Euro. Eine Strandbar. Ratet, was übrig bleibt.“ → **A gewählt** (Konsequenz-Hook = Gewinner von gestern, roter „0 €“-Kasten). B als Selbstironie-Zeile in der Mitte.
- Neue Optionen: 1 Brunnen · 2 Garten · 3 Mauer (Wunsch seal.medusa, 2 Likes).
- Technik: tag03b.py zoomt in Bau-/Pleite-Szene auf den Strand (zoomed(), z=1,75), damit der neue Bau groß zu sehen ist; Untertitel wandern dort auf y=1330 (sonst über dem Bau). Bauphase jetzt ~3,6 s mit eigener Bauteil-Liste (Sonnenschirm/Theke/Hocker) – Learning von T1 umgesetzt. strandbar() in bauten.py (x=70, Boden 1890). Unten links ist der Strand jetzt voll → nächster Bau braucht anderen Platz (z. B. Insel/Wald oder pan_view weiter links).
- Gepostet 21:00 Berlin, media_id 18102445040653370. 4 Kommentare beantwortet (3 Strandbar-Stimmen, Mauer-Wunsch seal.medusa). Kein Spam.

## 2026-11-12 15:00 – Tag 4 · Teil 1/2 (Mini-Mauer, 32 s)
- Zahlen vor dem Post: Tag 1 150 Views / 2 Likes / Skip 55 %. Tag 2·T1 1.214 / 33 / Skip 52 %. Tag 2·T2 (Bäckerei) 772 / 26 / 14 Kom. / **Skip 38 %** / Ø 12,1 s. Tag 3·T1 (Fischerhütte, ~24 h) 316 / 8 / 6 Kom. / Skip 43 % / Ø 8,3 s. Tag 3·T2 (Strandbar, ~18 h) 280 / 7 / 4 Kom. / Skip 54 % / Ø 8,5 s. Follower 15 (+1). Shares fast überall 0.
- Auswertung gestern: Like-Ziel-Mechanik („1 Like = 1 €“ groß) brachte **keine** höhere Like-Quote (T2 2,5 % vs. T1 2,5 %). Konsequenz-Hook „null Euro“ hielt schlechter (Skip 54 %) als die Bäckerei-Version – der Effekt nutzt sich ab. Reichweite fällt seit Tag 2 (1.214 → ~300).
- Abstimmung: 3× „3“ (seal.medusa, karstenffm, 041_sxcz_; 0 Likes), 1× „2“ + Wunsch Strandkörbe + „Wofür eine Mauer??“ (587pii) → Mauer. Kasse 1000 + 76 − 1065 = 11 € → Mini-Mauer −10 € → **1 €**.
- **Test des Tages: Humor-/Rätsel-Hook** statt Konsequenz-Hook (Befehl 3, Selbstironie). Varianten: (A) „Drei von euch wollten eine Mauer. Keiner hat gesagt, wofür.“ (B) „Ich hab elf Euro. Ihr wollt eine Mauer.“ (C) „Meine neue Mauer ist drei Steine hoch.“ → **A gewählt** (Frage im Kopf + Zuschauerkommentar von 587pii aufgegriffen). „WOFÜR?“ im roten Kasten ab 0,15 s. Pointe: „Sie ist drei Steine hoch. Selbst eine Katze steigt drüber.“ mit animierter Katze über der Mauer.
- Neue Optionen: 1 Brunnen · 2 Garten · 3 Strandkörbe (Wunsch 587pii).
- Technik: edge-tts lieferte für „Sechsundsiebzig Likes. Elf Euro.“ mehrfach NoAudioReceived → Satz umformuliert (Kommas statt Punkte) half; Zeilen einzeln mit Retry erzeugen. Pausen 0,15 s → 32,3 s. mauer()/katze() in bauten.py, Mauer bei x=380, Boden 1790. zoomed() verschiebt Ausschnitt auf x0=170. Kleiner Fehler: Untertitel-Rest („DRÜBER“) läuft 0,1 s in die Abstimmungsszene – harmlos.
- Nächstes Mal: Skip-Rate T1 heute vs. 43–54 % → Humor-Hook fest übernehmen, wenn < 45 %. Reichweite sinkt → Gewinner-Format (Bäckerei: Konsequenz + Pointe am Ende) mit neuem Humor kombinieren. Platz am Strand links ist voll → nächster Bau rechts (Fluss/Insel).
- Gepostet 15:00 Berlin, media_id 18101302799099828. 4 Kommentare beantwortet (3 Mauer-Stimmen, Strandkörbe-Wunsch). Kein Spam.

## 2026-11-12 21:00 – Tag 4 · Teil 2/2 (Mauer 2.0, 30,6 s)
- Zahlen vor dem Post: Tag 4·T1 (Mauer, ~5 h) 421 Views / 15 Likes / 5 Kom. / **Skip 44,8 %** / Ø 10,3 s – bestes Reel seit der Bäckerei (nach 5 h mehr als doppelt so viele Views wie Tag 3·T1). Tag 3·T1 333 / 10 / Skip 43 %. Tag 3·T2 311 / 8 / Skip 53 %. Likes gesamt 94, Follower 15 (±0).
- Ergebnis Test T1: **Humor-/Rätsel-Hook gewinnt** (Skip < 45 %, Likes-Quote 3,6 %). → Gewinner ausbauen: dieses Reel ist die direkte Fortsetzung (Mauer + Katze).
- Top-Kommentar: „Eine noch höhere Mauer“ (karstenffm, 2 Likes) → Mauer 3 → 6 Steine (−9 €). Kasse 1000 + 94 − 1075 = 19 € → **10 €**. Neuer Wunsch „Goldmine für mehr Geld“ (korosensei0815) als Option 2.
- **Test des Tages: Fortsetzungs-Hook mit Running Gag** (Katze aus T1). Varianten: (A) „Meine Mauer war euch zu niedrig.“ (B) „Ein Kommentar, zwei Likes: Die Mauer muss höher.“ (C) „Die Katze ist über meine Mauer gestiegen. Das war ein Fehler.“ → **C gewählt** (Bewegung ab Frame 0: Katze springt im Hook über die alte Mauer, roter Kasten „FEHLER!“). Pointe: „Die Katze geht einfach außen rum.“
- Auswerten morgen: Skip-Rate T2 vs. T1 (44,8 %). Wenn ≤ 45 %: Katze als wiederkehrende Figur behalten (Maskottchen-Potenzial).
- Technik: tts.py mit 4 Retries pro Zeile + SKIP_DONE=1 (fertige Zeilen überspringen). „Also: Stein vier…“ (Doppelpunkt) gab NoAudioReceived → Kommas helfen. Hook-Untertitel auf y=1150, sonst verdecken sie Mauer+Katze im Zoom.
- Gepostet 21:00 Berlin, media_id 18161475304503329. 4 Kommentare unter T1 beantwortet. Kein Spam.

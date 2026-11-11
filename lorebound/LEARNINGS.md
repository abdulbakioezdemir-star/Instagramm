# Lorebound – Learnings

## 2026-11-10 – Reel 13:00 „Fenrir – Die Fessel, die es nicht gibt“ (Mythen)
**Zahlen vorher (Windsor, 14 Tage):** Schachmatt (17930052021429811): 74 Views, 63 Reach, Skip-Rate 45 %, Ø Watch 6,0 s, 1 Save, 0 Likes/Shares/Kommentare.
Duplikat (gelöscht): 63 Views, Skip 67 %, Ø 3,5 s. followers_count lieferte 0 (vermutlich noch nicht aktualisiert).
**Erkenntnis:** Ø Watch 6 s bei 30 s Länge → Leute steigen nach dem Hook aus. Datenbasis noch winzig.

**Was ich diesmal gemacht habe:**
- Hook-Text steht ab Frame 0 (keine Einblendung) + Boom/Pauke auf Frame 0; Cover per thumb_offset 1500 ms.
- Alle 1–3 s ein neuer Reiz: Text-Karte, Kette reißt (8 s, 11 s), sechs „unmögliche Dinge“ je mit Glocke, Gleipnir, Hand, Stille, Drop (30 s).
- 0,5 s Stille vor dem Drop; Bild und Ton per `render.js verify` exakt synchron gemessen.
- Pipeline: Skill animation-studio (Canvas + synthetisierte Musik), Skripte unter lorebound/pipeline/fenrir/.
  Neu aufsetzen: `node <skill>/scripts/new-project.js <dir> --format 9:16`, dann score.js/song.js/film.js/index.html + fonts/ hineinkopieren,
  `LUFS=-13 node song.js && node engine/render.js video && node engine/render.js mux && node engine/render.js verify` (Render ≈ 5 min).
- Schriften Bebas Neue/Cinzel/Oswald via `npm pack @fontsource/...` (GitHub-Raw für fremde Repos ist im Sandbox gesperrt).
- Inhalt muss über der unteren 22 %-Zone bleiben (Instagram-UI): Wolfskopf wird in der Hand-Szene nach oben verschoben.

**Beim nächsten Mal prüfen:** Skip-Rate und Ø Watch-Time Fenrir vs. Schachmatt. Wenn Ø Watch < 10 s bleibt → kürzer (25–30 s) und Mittelteil straffen.
**Achtung:** Um 12:32 lief bereits ein Wissen-Reel („Papier bis zum Mond“, 18137974267678434) aus einem anderen Lauf – heute also schon 2 Reels bis 13 Uhr. 19-Uhr-Lauf: weder Wissen noch Mythen, lieber Fantasy oder Gleichnis. Jeder Lauf muss vor dem Posten die letzten Posts per Windsor prüfen.

## 2026-11-10 Analyse (Chat mit Besitzer, 17:30)
- Schachmatt: 91 Views, Skip 45 %. Papier→Mond (Wissen): 129 Views, Skip 61 %. Fenrir: 6 Views.
- Fenrir ging 26 Minuten nach Papier→Mond raus und ist untergegangen. **Nie zwei Reels innerhalb von 2 Stunden** auf diesem Konto;
  wenn das letzte Reel jünger als 2 h ist, bis zum Slot warten oder den Slot auslassen.
- 0 Follower trotz ~230 Views: Es fehlt ein Grund zum Folgen. **Ab sofort Serien-Rahmen**: oben eingeblendet und in Caption
  „Mythen in 30 Sekunden #N“, „Wissen in 30 Sekunden #N“ usw.; Schlusszeile: „Folge für Teil #N+1“.
- Skip-Raten 45–61 %: erste Sekunde muss eine überraschende Behauptung + starkes Bild sein (wie „ER HATTE ALLES.“).

## 2026-11-10 – Reel 19:00 „Der hundertste Schlag“ (Gleichnis, Serie „Gleichnisse in 30 Sekunden #1“)
**Zahlen vorher (Windsor, 16:35 UTC):** Papier→Mond 129 Views / Skip 61 % / Ø 6,9 s; Schachmatt 91 / 45 % / Ø 6,7 s / 1 Save; Fenrir 7 / 57 % / Ø 3,8 s. Follower 0. Keine Kommentare.
**Wahl:** Gleichnis, weil Schachmatt (Gleichnis) die beste Skip-Rate hatte und heute schon Wissen + Mythos liefen.
**Hook-Varianten (Befehl 3):** a) „99 Schläge. Kein Riss.“ b) „Alle lachten über ihn. Zu früh.“ c) „Dieser Stein hielt 99 Schläge aus.“ → a) gewählt (4 Wörter, Zahl + Widerspruch, Hammerschlag + Kamerawackeln auf Frame 0).
**Test des Tages:** Serien-Rahmen erstmals im Bild („GLEICHNISSE IN 30 SEKUNDEN · #1“ oben, Schluss-Tafel „FOLGE FÜR TEIL #2“) + sichtbarer Zähler „SCHLAG 1 … 100“ als Grund zum Dranbleiben. Ziel: Ø Watch > 10 s und erster Follower.
**Trockene Zeile:** „Er nickte höflich. Und schlug weiter.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert, -13 LUFS, Drop bei 22,0 s per verify exakt synchron. Jeder der 28 Hammerschläge ist ein Ton (Stein-Knock + Metall), Lautstärke wächst mit dem Zähler. Hammer horizontal von rechts (Schwung-Drehpunkt außerhalb des Bildes war unsichtbar) – Stein dafür 70 px nach links.
**Gepostet:** 18:00:40 UTC (19:00 Berlin), media_id 18141305875618889, https://www.instagram.com/reel/Dfkf_1qlHZ9/ – Fenrir lag kurz vorher bei 10 Views (Skip 60 %).
**Nächstes Mal prüfen:** Skip-Rate/Ø Watch vs. Schachmatt; ob der Zähler die Watch-Time hebt. Wenn ja: Zähler/Countdown-Motiv auch in Mythen/Wissen nutzen.

## 2026-11-11 – Reel 13:00 „Sisyphos – Er betrog den Tod“ (Mythen, Serie „Mythen in 30 Sekunden #1“)
**Zahlen vorher (Windsor, 10:35 UTC, 14 Tage):** Hundertster Schlag 156 Views / Reach 134 / **Skip 37 % / Ø 10,5 s** (bester Wert bisher); Papier→Mond 130 / 61 % / 6,8 s; Schachmatt 105 / 50 % / 6,2 s / 1 Save; Fenrir 41 / 58 % / 7,4 s. Follower 0, keine Likes/Shares/Kommentare.
**Erkenntnis:** Zähler-Motiv + Serien-Rahmen (Hundertster Schlag) hat Skip-Rate um ~15 Punkte gesenkt und Ø Watch über 10 s gehoben → **Gewinner ausbauen**.
**Wahl:** Mythos (letztes Reel war Gleichnis), aber mit dem Gewinner-Bauplan: sichtbarer Zähler „VERSUCH 1 … 9.999 → ∞“, Serien-Tag oben, „FOLGE FÜR TEIL #2“ am Ende.
**Hook-Varianten:** a) „Er betrog den Tod.“ b) „Dieser König legte den Tod in Ketten.“ c) „Seine Strafe: für immer.“ → a) (4 Wörter, Behauptung, Ketten schnappen auf Frame 0 zu + Boom + Kamerawackeln).
**Test des Tages:** Funktioniert der Zähler auch außerhalb der Gleichnis-Serie (Mythos)? Vergleich Skip/Ø Watch mit Hundertster Schlag. Zusätzlich: erstmals Frage an Zuschauer in der Caption („Wärst du an seiner Stelle glücklich?“) → Kommentare?
**Trockene Zeile:** „Fast oben? Immer nur fast.“ Schluss: Camus-Zitat (1942) – starke, zitierfähige Schlusszeile.
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (-12,9 LUFS), Drop 22,0 s per verify exakt synchron. Akt 1 (0–8 s) Tod in Ketten, „eingefrorene Zeit“ (Partikel stehen 4–6 s still, Herzschlag setzt aus), Akt 2 Berg im Zeitraffer (8 Schub-Zyklen, immer kürzer). Figur: Füße 380 px hangabwärts vom Felskontakt, 35° Neigung, sonst verdeckt der Fels sie. Bergspitze bei H·0,47, damit stehende Figur nicht in die Texttafeln ragt. Kartenausblendung 0,1 s statt 0,25 s (sonst überlappen Tafeln).
**Gepostet:** 11:57 UTC (12:57 Berlin), media_id 18098604404136628, https://www.instagram.com/reel/DfmbLmiDyYj/
**Nächstes Mal prüfen:** Sisyphos vs. Hundertster Schlag (Skip, Ø Watch). Wenn Sisyphos ≥ ähnlich gut: Zähler wird Standard für alle Kategorien. 19-Uhr-Lauf heute: weder Mythen noch Gleichnis → Wissen oder Fantasy.

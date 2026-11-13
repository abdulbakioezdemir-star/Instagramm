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

## 2026-11-11 – Reel 19:00 „Ein Tag länger als ein Jahr“ (Wissen, Serie „Wissen in 30 Sekunden #1“)
**Zahlen vorher (Windsor, 16:35 UTC, 14 Tage):** Hundertster Schlag 175 Views / Reach 149 / **Skip 35 % / Ø 11,1 s** (weiter klar bester); Papier→Mond 132 / 62 % / 6,7 s; Schachmatt 105 / 50 % / 6,2 s / 1 Save; Fenrir 53 / 53 % / 9,6 s; **Sisyphos 65 / 53 % / Ø 5,6 s** (nach ~5 h). Follower 0, keine Likes/Shares/Kommentare (also nichts zu beantworten).
**Erkenntnis:** Der Zähler allein hat Sisyphos nicht gerettet → beim Gewinner wirkte vermutlich eher das **einfache, sofort verständliche Bild** (Stein + Hammer, ein Ding im Fokus) plus Zähler. Sisyphos war visuell komplexer (Ketten, Tod, Berg) und der Hook „Er betrog den Tod“ braucht Vorwissen.
**Wahl:** Wissen (heute schon Mythos; gestern Gleichnis). Fakt geprüft: Venus-Rotation 243 Erdtage (rückläufig), Umlauf 224,7 Erdtage (NASA/Britannica u. a.). Bewusst „eine Drehung um sich selbst“ gesagt (Sonnentag wäre ~117 Tage).
**Hook-Varianten:** a) „Hier ist ein Tag länger als ein Jahr.“ b) „Auf diesem Planeten ist Silvester vor Feierabend.“ c) „Dieser Planet dreht sich falsch herum.“ → a) (7 Wörter, Paradox, Planet groß + Flash + Boom auf Frame 0). b) als trockene Pointe ans Ende.
**Test des Tages:** **Wettrennen statt Zähler allein** – zwei Fortschrittsbalken „EIN JAHR“ vs. „EIN TAG“ + Zähler „ERDTAG 1…243“; Jahr gewinnt bei 14 s, dann quälend langsames Weiterzählen bis 243 (Drop 20 s). Frage: hält ein sichtbares „Rennen“ mit offenem Ausgang die Leute bis zum Drop?
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (-12,8 LUFS), jeder Zählschritt = Marimba-Ton (E-Moll aufsteigend), Jahr-Ende = Glockenakkord, 0,5 s Stille vor dem Drop; verify: 14,0 s und 20,0 s exakt synchron. Cover thumb_offset 1500 ms.
**Gepostet:** 18:00:21 UTC (19:00 Berlin), media_id 18147484315606747, https://www.instagram.com/reel/DfnExBdDb1Z/
**Nächstes Mal prüfen:** Venus vs. Hundertster Schlag vs. Papier→Mond (anderes Wissen-Reel ohne Zähler/Serie). Wenn Venus Skip < 45 %: Format „Wettrennen/Zähler + ein klares Objekt“ wird Standard. Wenn Sisyphos weiter schwach bleibt: Mythen-Hooks ohne Vorwissen formulieren (z. B. „Dieser Mann sperrte den Tod in eine Kiste.“).

## 2026-11-12 – Reel 13:00 „Der Bambus“ (Gleichnis, Serie „Gleichnisse in 30 Sekunden #2“)
**Zahlen vorher (Windsor, 10:35 UTC, 14 Tage, Cache):** Hundertster Schlag 180 Views / Reach 153 / **Skip 34 % / Ø 11,2 s** (weiter Spitze); Sisyphos 115 / 50 % / 6,2 s; Papier→Mond 132 / 62 % / 6,7 s; Schachmatt 105 / 50 % / 6,2 s / 1 Save; Fenrir 53 / 53 % / 9,6 s; **Venus 3 Views / Skip 100 % nach ~16 h** (wie gestern Abend gemeldet – entweder Cache-Problem oder kaum ausgespielt; beim nächsten Lauf erneut prüfen). Follower 0, keine Likes/Shares/Kommentare (nichts zu beantworten).
**Wahl:** Gewinner ausbauen → Gleichnis #2 (letztes Reel war Wissen). Bauplan wie Hundertster Schlag: **ein einfaches Objekt** (Keimling), sichtbarer Zähler, Serien-Tag, „Folge für Teil #3“.
**Fakten (Websuche):** Moso-Bambus (Phyllostachys edulis) wächst bis zu ~1 m/Tag, erreicht in ca. 2 Monaten volle Höhe (>20 m); vorher Jahre Rhizom-/Wurzelaufbau. Bewusst ohne exakte „5 Jahre“-Behauptung formuliert („Jahrelang“).
**Hook-Varianten:** a) „Jahrelang: nichts.“ b) „4 Jahre. Kein Zentimeter.“ c) „Alle hielten ihn für tot.“ → a) (2 Wörter, Widerspruch, Wassertropfen + Boom + Flash auf Frame 0). c) als trockene Zeile („„Der ist tot“, sagte der Nachbar.“ + „Jedes Jahr.“).
**Test des Tages:** **Zähler-Wechsel als Twist** – erst „TAG 1 … 1.460“ (langsam, Geduld), nach dem Drop „METER 1 … 20“ (schnell, Belohnung). Plus Kamera-Schwenk unter die Erde (goldenes Wurzelnetz) als Mitte-Reveal bei 12 s. Frage: hält ein Perspektivwechsel in der Mitte die Ø Watch über 11 s?
**Schluss:** „Du bist nicht zu langsam. Du wächst nach unten.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (-12,9 LUFS, Peak -1,4 dBFS); jeder Tag = Tropfen + Marimba (D-Moll-pentatonisch), jeder Meter = steigende Marimba + Holz-Knacken; Drop 18,0 s per verify exakt synchron. Mond nicht oben rechts neben die Texttafeln setzen (überlappte) → H·0,40. Zähler nach dem Drop mit dunkler Box, weil der Halm durch ihn läuft. Outro-Abdunklung 0,55, sonst stört der Halm die Schlusszeile.
**Gepostet:** 12:00 UTC (13:00 Berlin), media_id 17989900539091476, https://www.instagram.com/reel/DfpAVlvDyfW/
**Nächstes Mal prüfen:** Bambus vs. Hundertster Schlag (Skip, Ø Watch). Wenn beide Gleichnisse vorne liegen: Gleichnis-Serie öfter (z. B. jeden Tag ein Slot), Mythen/Wissen mit gleichem Bauplan (ein Objekt + Zähler) neu formulieren. Venus-Zahlen nachprüfen.

## 2026-11-12 – Reel 19:00 „Die leere Truhe“ (Fantasy, Serie „Fantasy in 30 Sekunden #1“)
**Zahlen vorher (Windsor, 17:45 UTC, Cache):** **Bambus 122 Views / Skip 26 % / Ø 10,5 s nach ~6 h** (beste Skip-Rate bisher); Hundertster Schlag 180 / 34 % / 11,2 s; Sisyphos 115 / 50 % / 6,2 s; Papier→Mond 132 / 62 % / 6,7 s; Schachmatt 105 / 50 % / 6,2 s; Fenrir 53 / 53 % / 9,6 s; Venus 7 / 60 % / 6,3 s (nach 24 h – praktisch nicht ausgespielt). Follower 0, keine Kommentare/Likes/Shares (nichts zu beantworten).
**Erkenntnis:** Beide Gleichnisse (ein Objekt + Zähler + Serie) liegen klar vorne (Skip 26–34 %, Ø > 10 s). Mythen/Wissen ohne diese Klarheit bei 50–62 % Skip.
**Wahl:** Fantasy (heute 13:00 schon Gleichnis; Fantasy noch nie getestet), aber im Gewinner-Bauplan: **ein Objekt (Truhe)**, Zähler „JAHR 1 … 1.000“, Serien-Tag, „Folge für Teil #2“. Eigene Geschichte, keine geschützten Figuren.
**Hook-Varianten:** a) „Er bewachte 1.000 Jahre: nichts.“ b) „1.000 Jahre. Eine leere Truhe.“ c) „Kein Ritter überlebte diese Truhe.“ → b) (6 Wörter, Zahl + Widerspruch; Drachenauge öffnet sich + Boom auf Frame 0).
**Test des Tages:** Funktioniert der Gewinner-Bauplan (Objekt + Zähler) auch für **erzählte Fantasy mit Dialog und Twist** („Darf ich mal gucken?“ → Truhe leer → Dorf hinter dem Drachen)? Vergleich Skip/Ø Watch mit Bambus/Hundertster Schlag.
**Trockene Zeile:** „Ritter kamen. Ritter rannten.“ + „Darf ich mal gucken?“ Schluss: „Er bewachte nichts. Und schützte alles.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (-12,9 LUFS, Peak -1,3 dBFS), jedes Jahr = Marimba-Münzton, Ritter = Feuer-Whoosh + Thud, Kind = Schritte, 0,5 s Stille vor dem Drop (16,0 s, verify exakt synchron). Grund-Zoom 1,14 (sonst wirkt die Szene klein); Dorf rechts hinter dem Drachen (passt zum Text „Hinter ihm“).
**Gepostet:** 18:00 UTC (19:00 Berlin), media_id 17971737360195477, Cover thumb_offset 1500 ms.
**Nächstes Mal prüfen:** Truhe vs. Bambus. Wenn Fantasy mit Bauplan ≤ 35 % Skip: Fantasy-Serie fortsetzen (Teil #2). Venus-Reel wurde kaum ausgespielt – Ursache unklar (evtl. Reichweitenproblem einzelner Posts); weiter beobachten.

## 2026-11-13 – Reel 13:00 „Das dünne Seil“ (Gleichnis, Serie „Gleichnisse in 30 Sekunden #3“)
**Ab heute (Befehl 5): nur 1 Reel/Tag um 13:00.** Der 19:00-Lauf postet nicht mehr.
**Zahlen vorher (Windsor, 10:40 UTC, 14 Tage, Cache):** **Bambus 275 Views / Reach 230 / Skip 27,5 % / Ø 12,6 s / 1 Save / 1 Like** (neuer Bestwert); Hundertster Schlag 180 / 34 % / 11,2 s; Truhe (Fantasy) 120 / 57 % / 7,9 s / 1 Like; Sisyphos 117 / 50 % / 6,1 s; Papier→Mond 132 / 62 % / 6,7 s; Schachmatt 105 / 50 % / 6,2 s; Fenrir 53 / 53 % / 9,6 s; Venus 7. Follower 0 (Windsor). Keine Kommentare (nichts zu beantworten).
**Erkenntnis:** Gleichnisse schlagen alles andere deutlich (Skip 27–34 % vs. 50–62 %). Fantasy mit Bauplan (Truhe) hat nicht geholfen → der Gewinner ist **Gleichnis + ein Objekt + Zähler**, nicht der Zähler allein.
**Wahl:** Gewinner ausbauen → Gleichnis #3 (letztes Reel war Fantasy, also Kategorie gewechselt). Klassisches Gleichnis vom angebundenen Elefanten (als Gleichnis erzählt, keine Tatsachenbehauptung). „4 Tonnen“ = untere Spanne eines asiatischen Elefantenbullen (geprüft).
**Hook-Varianten:** a) „4 Tonnen. Ein dünnes Seil.“ b) „Dieses Seil hält einen Elefanten. Warum?“ c) „Er könnte jederzeit gehen.“ → a) (5 Wörter, Zahl + Widerspruch, Seil spannt sich + Boom + Flash auf Frame 0).
**Test des Tages:** **Frage an die Zuschauer als Schlusszeile im Bild** („WELCHES SEIL HÄLT DICH NOCH?“) + gleiche Frage in der Caption → bringt das die ersten Kommentare? Zusätzlich: Zähler, der „stirbt“ (VERSUCH 1 … 1.000 wird grau und durchgestrichen) und dann als „JAHR 1 … 20“ weiterläuft.
**Trockene Zeile:** „Er versucht es nicht mal.“ Schluss-Twist: „Ihn hält kein Seil. Ihn hält eine Erinnerung.“ (Seil zerfällt beim Drop zu Goldstaub).
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (-12,8 LUFS), jedes Ziehen = Thud + Marimba (wird schwächer), jedes Jahr = steigende Marimba, 0,5 s Stille vor dem Drop (20,0 s, verify exakt synchron). Elefant aus Ellipsen + Bezier-Rüssel (70 Punkte, sonst wirkt der Gold-Rand gepunktet); Gold-Rand-Trick: erst alle Teile mit breitem Gold-Stroke, dann dunkle Füllung darüber → nur die Silhouette glüht. Rückblende = Sepia-Multiply-Schleier. Render ≈ 3 min.
**Gepostet:** 12:00:52 UTC (13:00 Berlin), media_id 18139798480730537, https://www.instagram.com/reel/DfrlM8HjDnO/, Cover thumb_offset 1500 ms. Bambus lag kurz vorher bei 349 Views.
**Nächstes Mal prüfen:** Seil vs. Bambus (Skip, Ø Watch) und ob Kommentare auf die Frage kommen. Da nur noch 1 Reel/Tag: Gleichnis ist der Gewinner – Kategorie trotzdem wechseln (LOREBOUND.md), aber Mythen/Wissen streng im Gleichnis-Bauplan (ein Objekt, Zähler, Hook ohne Vorwissen, Lehre am Ende).

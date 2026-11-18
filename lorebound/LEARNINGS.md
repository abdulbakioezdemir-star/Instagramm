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

## 2026-11-14 – Reel 13:00 „Das Schwert des Damokles“ (Mythen, Serie „Mythen in 30 Sekunden #2“)
**Zahlen vorher (Windsor, 10:40 UTC, 14 Tage, Cache):** **Seil 1.303 Views / Reach 1.191 / Skip 24,1 % / Ø 15,4 s / 19 Likes / 2 Saves** nach ~23 h – mit Abstand bester Wert (3× Bambus). Bambus 386 / 27,6 % / 12,8 s / 3 Saves / 2 Likes; Hundertster Schlag 180 / 34 % / 11,2 s; Papier→Mond 132 / 62 %; Truhe 120 / 57 %; Sisyphos 117 / 50 %; Schachmatt 105 / 50 %; Fenrir 62 / 54 %; Venus 10. **Follower: 1** (erster!). Keine Kommentare – auch nicht auf die Frage im Seil-Reel (Frage im Bild bringt Likes/Watch, aber keine Kommentare).
**Erkenntnis:** Der Seil-Hook „4 TONNEN. EIN DÜNNES SEIL.“ (riesige Last ↔ winziger Halt) + Lehre am Ende ist das stärkste Muster bisher.
**Wahl:** Kategorie wechseln (letztes = Gleichnis) → **Mythos, aber als Variante des Gewinner-Hooks**: Damokles – ein Schwert an einem einzigen Pferdehaar über dem Thron. Sage nach Cicero (Gespräche in Tusculum V 61–62, geprüft via livius.org/history.com); König nur als „der König“, ohne Namensstreit Dionysios I./II.
**Hook-Varianten:** a) „Ein Schwert. Ein einziges Haar.“ b) „Er saß auf dem Thron. Und zitterte.“ c) „Alle wollten seinen Platz. Bis er hochsah.“ → a) (5 Wörter, gleiche Bauart wie Seil: großes Ding ↔ winziger Halt; Schwert schwingt + Boom + Glanz auf Frame 0).
**Test des Tages:** Trägt der Gewinner-Hook (Last ↔ dünner Halt) auch in der Kategorie Mythen? Vergleich mit Seil/Bambus und Sisyphos (Mythos #1, 50 % Skip). Zusätzlich: Schluss als **Aussage** („BENEIDE KEINEN THRON.“) statt Frage, Frage nur in der Caption.
**Zähler:** „PULS 72 → 180“ (Herzschlag beschleunigt, jeder Schlag = Heartbeat-Sound + roter Vignetten-Puls), statt Versuche/Jahre.
**Trockene Zeile:** „DAS FESTMAHL WURDE KALT.“ (Dampf über dem Essen hört auf, Trauben werden grau). Lehre: „WER DIE KRONE WILL, BEKOMMT DAS SCHWERT DAZU.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (D-Moll, -12,9 LUFS, Peak -1,0 dB), Marimba-Arpeggien im Prunk-Teil, Glocken-„Schwertklang“ (bell ratio 2.76) bei Hook/Reveal/Drop; verify: Reveal 12,0 s und Drop 20,0 s exakt synchron. Schwert nur im Hook und ab „Dann sah er nach oben“ sichtbar (Reveal mit Lichtkegel + Flash). Schwertspitze ~55 px über dem Kopf. Render ≈ 4,5 min. `chordAt().notes` liefert MIDI-Zahlen, nicht Notennamen.
**Gepostet:** 12:01 UTC (13:01 Berlin), media_id 18659532328013276, https://www.instagram.com/reel/DfuJ_mDAkRd/, Cover thumb_offset 1500 ms. Seil lag kurz vorher bei 1.306 Views.
**Nächstes Mal prüfen:** Damokles vs. Seil/Bambus/Sisyphos (Skip, Ø Watch, Likes). Wenn Damokles ≤ 30 % Skip: Gewinner-Hook „große Last ↔ winziger Halt“ wird Standard für alle Kategorien. Kommentare kamen bisher nie – evtl. Kommentar-Anreiz testen (z. B. „Schreib ein Wort: …“).

## 2026-11-15 – 19:00-Lauf (Befehl 5: kein Reel)
Nichts gerendert/gepostet (Befehl 5). Keine Kommentare zu beantworten (Windsor, 14 Tage, 0 Kommentare). **Auffällig:** Kein Lorebound-Reel am 15.11. – der 13:00-Lauf hat weder gepostet noch committet (Windsor-Cache zeigt nur Seil 1.311 und Damokles 146 Views). Muss vom 13:00-Bot/Besitzer geprüft werden.

## 2026-11-16 – Reel 13:00 „Das Glas Wasser“ (Gleichnis, Serie „Gleichnisse in 30 Sekunden #4“)
**Zahlen vorher (Windsor, 10:40 UTC, 14 Tage, Cache):** Seil 1.311 Views / Reach 1.200 / Skip 24,5 % / Ø 15,4 s / 19 Likes / 2 Saves (weiter Spitze); Bambus 387 / 27,8 % / 12,8 s / 3 Saves; Hundertster Schlag 180 / 34 %; **Damokles (Mythos #2) 147 / 43 % / Ø 10,4 s / 1 Like** – besser als Sisyphos (50 %), aber klar unter den Gleichnissen; Truhe 120 / 57 %; Sisyphos 117 / 50 %; Papier→Mond 132 / 62 %; Schachmatt 105 / 50 %; Fenrir 62 / 54 %; Venus 10. Follower 2. Kommentare: 0 (nichts zu beantworten/auszublenden). 15.11.: kein Reel (Lauf FAILED, USAGE_LIMIT_REACHED).
**Erkenntnis:** Der Last↔Halt-Hook trägt in Mythen nur halb (Damokles 43 % Skip). Der Gewinner bleibt **Gleichnis + ein Objekt + Zähler + Lehre**.
**Wahl:** Kategorie gewechselt (letztes = Mythos) → Gleichnis #4: das bekannte Stress-Gleichnis vom Glas Wasser (Gewicht bleibt gleich, die Dauer macht es schwer; als Gleichnis erzählt, Quelle: verbreitete „Weight of the Glass“-Weisheitsgeschichte, keine reale Person genannt).
**Hook-Varianten:** a) „250 GRAMM. ZU SCHWER.“ b) „Dieses Glas hat mich besiegt.“ c) „Halt es. Nur einen Tag.“ → a) (Bauart wie Seil: Zahl + Widerspruch, kleines Ding ↔ riesige Last; Glas schwappt + Boom + Glas-Klang auf Frame 0).
**Test des Tages:** **Kommentar-Anreiz mit einem Wort** – Schluss-Tafel „SCHREIB »ABGESTELLT«, WENN DU ES TUST“ + gleiche Bitte in der Caption (statt offener Frage wie beim Seil). Bringt ein Ein-Wort-Kommentar die ersten Kommentare?
**Zähler:** „MINUTE 1 … 60“ (ruhig, Gold) → „STUNDE 1 … 24“ (wird rot, Arm glüht rot, Glas zittert/sinkt, Wasser schwappt über).
**Trockene Zeile:** „DAS GLAS WURDE NIE SCHWERER.“ Lehre: „NICHT DAS GEWICHT BRICHT DICH. SONDERN DIE DAUER.“ Schluss: „STELL ES HEUTE ABEND AB.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (D-Moll, -12,9 LUFS, Peak -0,6 dBFS), Glas-„Klink“ = bell ratio 2.76; Minuten = Marimba aufwärts + leiser Tick, Stunden = schwerer Tick-Tack + Thud + Marimba abwärts, Herzschlag ab „Einen Tag“; Drop 20,0 s = Glas setzt auf dem Tisch auf (Fall mit Beschleunigung in der Atempause) – verify exakt synchron. Hand: Handfläche hinter, Finger vor dem Glas (zwei Zeichenpässe), ctx.scale(1.3) für die Hand. Glas groß (390 px) – erster Entwurf mit 290 px wirkte leer. Render ≈ 3,5 min.
**Gepostet:** 12:00:46 UTC (13:00 Berlin), media_id 17943235728392375, https://www.instagram.com/reel/DfzTjq0HzE9/, Cover thumb_offset 1500 ms.
**Nächstes Mal prüfen:** Glas vs. Seil/Bambus (Skip, Ø Watch, Likes) und ob „ABGESTELLT“-Kommentare kommen (falls ja: jedem kurz antworten, Ein-Wort-Anreiz wird Standard). Nächstes Reel: Kategorie wechseln (Wissen oder Fantasy), aber streng im Gleichnis-Bauplan mit Lehre am Ende.

## 2026-11-17 – Reel 13:00 „Der Riese, der auf Feuer wartet“ (Wissen, Serie „Wissen in 30 Sekunden #2“)
**Zahlen vorher (Windsor, ~10:35 UTC, 14 Tage, Cache):** Seil 1.312 Views / Skip 24,5 % / Ø 15,3 s / 19 Likes (Spitze); Bambus 387 / 27,8 % / 12,8 s; Hundertster Schlag 180 / 34 %; Damokles 147 / 43 % / 10,4 s; **Glas Wasser (Gleichnis #4) nur 119 / Reach 111 / Skip 40,5 % / Ø 6,1 s nach ~22 h** – schwächstes Gleichnis. Follower 2. Kommentare: 0 überall (auch kein „ABGESTELLT“ → Ein-Wort-Kommentar-Anreiz hat nicht funktioniert; nichts zu beantworten/auszublenden).
**Erkenntnis:** Gleichnis allein garantiert nichts (Glas 40 % Skip). Seil/Bambus hatten ein **sichtbares, sofort verständliches Rätsel** (riesig ↔ winzig, Jahre nichts ↔ plötzlich riesig); beim Glas war die Pointe vorhersehbar. Kommentar-Anreize bringen bei 2 Followern nichts → stattdessen auf Saves zielen.
**Wahl:** Kategorie gewechselt (letztes = Gleichnis) → Wissen im Gleichnis-Bauplan: Mammutbaum (Sequoiadendron), Zapfen bleiben jahrelang (bis ~20 J.) geschlossen, Hitze von Feuer öffnet sie; Samen „klein wie Haferflocken“ (USGS/NPS geprüft), bis 3.000+ Jahre alt.
**Hook-Varianten:** a) „DIESER RIESE WARTET AUF FEUER.“ b) „20 JAHRE GESCHLOSSEN. DANN: FEUER.“ c) „Ein Samen wie eine Haferflocke. 90 Meter.“ → a) (5 Wörter, Paradox; Flammen + Glut + Boom auf Frame 0).
**Test des Tages:** **Speicher-Anreiz statt Kommentar-Anreiz** („SPEICHERN FÜR EINEN SCHWEREN TAG“ im Bild + Caption) und Wissen mit Lehre („MANCHES IN DIR ÖFFNET SICH ERST IM FEUER.“). Messen: Saves, Skip vs. Venus/Papier (Wissen ohne Lehre, 61–67 %).
**Zähler:** „JAHR 1 … 20 · ZAPFEN: GESCHLOSSEN“ (Schnee-/Jahreszeiten-Partikel) → Hitze-Balken → Drop 18,0 s: Zapfen platzt auf, 46 goldene Samen fliegen, landen in der Asche, Keimlinge wachsen.
**Trockene Zeile:** „SOMMER. WINTER. NICHTS.“ Schluss: „DEIN FEUER IST NICHT DEIN ENDE.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (E-Moll, -12,9 LUFS, Peak -1,2 dBFS), Knistern = viele I.pop() mit Zufallstonhöhe, Brand-Rauschen = noiseSweep 120→900 Hz; verify Drop exakt synchron. Flammen mit 'lighter' + 3 Schichten: innere Schicht max. Alpha 0,22, sonst wird der Boden weiß ausgebrannt. Zähler mit dunkler Box (Flammen laufen dahinter). Render ≈ 4 min.
**Gepostet:** 12:00:37 UTC (13:00 Berlin), media_id 18112829990214057, https://www.instagram.com/reel/Df14W7UGTA0/, Cover thumb_offset 1500 ms.
**Nächstes Mal prüfen:** Mammutbaum vs. Seil/Bambus/Glas (Skip, Ø Watch, **Saves**). Wenn Saves > 2: Speicher-Anreiz bleibt Standard. Nächstes Reel: Kategorie wechseln (Fantasy oder Mythos), Hook mit sichtbarem Rätsel „riesig ↔ winzig“ wie beim Seil.

## 2026-11-18 – Reel 13:00 „Das Tor – 1.000 Ritter. Ein Kind.“ (Fantasy, Serie „Fantasy in 30 Sekunden #2“)
**Zahlen vorher (Windsor, ~10:35 UTC, 14 Tage, Cache):** Seil 1.313 / Skip 24,5 % / Ø 15,3 s (Spitze); Bambus 387 / 27,8 % / 3 Saves; **Mammutbaum (Wissen #2, Speicher-Anreiz) 136 / Reach 129 / Skip 40 % / Ø 8,1 s / 0 Saves** nach ~22 h; Glas 119 / 40,5 %. Follower 2. Kommentare überall 0 → nichts zu beantworten/auszublenden.
**Erkenntnis:** Speicher-Anreiz brachte 0 Saves → kein Standard. Seit dem Seil liegen alle Reels bei 40 % Skip / ~120–150 Views; Rätsel „riesig ↔ winzig“ fehlte zuletzt.
**Wahl:** Kategorie gewechselt (letztes = Wissen) → Fantasy im Gleichnis-Bauplan, eigene Geschichte: 1.000 Ritter rammen ein Tor, ein Kind liest die Inschrift „ZIEHEN“ (Alltags-Pointe: Drück-/Zieh-Tür, Befehl 3).
**Hook-Varianten:** a) „1.000 RITTER. EIN KIND.“ b) „Dieses Tor besiegte 1.000 Ritter.“ c) „300 Jahre zu. Dann kam ein Kind.“ → a) (4 Wörter, riesig ↔ winzig wie beim Seil; drei Ritter prallen am Tor ab + Boom auf Frame 0).
**Test des Tages:** **Share-Anreiz** („SCHICK ES JEMANDEM, DER IMMER DRÜCKT“ im Schluss-Tafel) + **Rewatch-Detail**: Die Inschrift „ZIEHEN“ steht ab Sekunde 0 halb unter Moos über dem Tor; Caption fragt „Hast du die Inschrift schon beim ersten Mal gesehen?“. Messen: Shares (bisher überall 0), Ø Watch, Kommentare.
**Zähler:** „RITTER 1 … 1.000 · TOR: ZU“ (22 Anstürme, immer schneller, jeder ein Treffer-Sound; Armee an den Seiten wächst), Blitz bei 10 s, Drachenfeuer bei 11 s, „TOR: ZU“ wird rot.
**Trockene Zeile:** „1.000 RITTER HATTEN GEDRÜCKT.“ Lehre: „NICHT JEDE TÜR BRAUCHT MEHR KRAFT. MANCHE NUR EINEN ZWEITEN BLICK.“ Schluss: „LIES, WAS DRANSTEHT.“
**Technik:** 30,0 s, animation-studio, Musik synthetisiert (D-Moll → D-Dur nach dem Drop, -12,9 LUFS), Drop 18,0 s (Tor schwingt nach außen auf, goldenes Licht) – verify exakt synchron. Türflügel-Perspektive: Tür-Textur einmal in init() auf Offscreen-Canvas, dann in 36 senkrechten Streifen mit wachsender Höhe gezeichnet (Trapez ohne WebGL). 4-zeilige Lehre-Karte überlappte den Torbalken → auf 3 Zeilen gekürzt. Render ≈ 3 min.
**Gepostet:** 12:00:37 UTC (13:00 Berlin), media_id 18134106115699938, https://www.instagram.com/reel/Df4dJ7zCbrk/, Cover thumb_offset 1500 ms.
**Nächstes Mal prüfen:** Tor vs. Seil/Mammutbaum (Skip, Ø Watch, **Shares**, Kommentare zur Inschrift). Wenn Shares > 0 oder Skip < 35 %: Alltags-Pointe + Share-Anreiz beibehalten. Nächstes Reel: Kategorie wechseln (Gleichnis oder Mythos).

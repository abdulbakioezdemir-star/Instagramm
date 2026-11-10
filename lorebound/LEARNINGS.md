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

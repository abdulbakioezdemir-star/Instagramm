# Nations-Serie „Valmora“ – Konto @ahmed.sucht.liebe (wird umbenannt)

Windsor-Account-ID: 17841459168444268 (connector `instagram`). Format: **Reels** (create_video_post, share_to_feed true).
Entschieden vom Besitzer am 2026-11-09: Konto komplett umbauen, Nation mit den Zuschauern gründen, voll automatisch.

## Idee (Vorbild: „Auravale“-Reels)
Der Erzähler gründet ein eigenes Land an einem Ort mit **Bergen und Meer** und ist der erste Einwohner.
Die Zuschauer bauen es mit auf:
- **Startkapital 1.000 €** (Staatskasse, fiktiv).
- **Jedes Like = 1 €** in die Staatskasse.
- **Jeder Follower = 1 Einwohner.**
- **Der Top-Kommentar** (meiste Likes) unter dem letzten Reel bestimmt, was im nächsten Video passiert
  (gebaut, beschlossen, entdeckt …). Kosten werden von der Staatskasse abgezogen.
- Name „Valmora“ und Flagge sind der Start-Vorschlag; die Zuschauer dürfen per Top-Kommentar umbenennen/neue Flagge fordern.

## Aufbau nach Vorbild-Video (Auravale)
Großes, leeres Gebiet zeigen (Kamerafahrt über Berge, Wälder, Fluss, Meer), Karte mit Grenzen und Fläche (12 km²),
Flagge, Startwerte-Tafel, sichtbarer Bau mit Fortschrittsbalken und Kosten, Budget-Tafel (alt − Kosten = neu),
Regeln, OG-Pass für die ersten 100 Einwohner. Welt: nation/pipeline/world.py (Panorama 3600×1920 + Karte).
Neue Bauten werden in Panorama/Karte eingezeichnet und bleiben in allen späteren Folgen sichtbar.

## Jedes Reel
- 1080×1920, 30–50 s, animiert im Stil der Pipeline (pipeline/), eigene Erzählerstimme (edge-tts, ruhig-episch, normal klingend).
- Hook in Sekunde 0–1 („Tag N meiner eigenen Nation …“), Anzeige oben: Staatskasse € · Einwohner · Tag N.
- Zeigen, was der Top-Kommentar gewünscht hat (Name des Kommentators nennen = Anreiz zum Kommentieren), Kosten abziehen.
- Ende: „Der Top-Kommentar entscheidet, was ich als Nächstes baue. Folgen = Einwohner werden.“
- **Zwei Reels pro Tag** (Wunsch Besitzer 2026-11-10): 15:00 = Tag N · Teil 1/2, 21:00 = Tag N · Teil 2/2.
  Jedes Reel setzt den Top-Kommentar unter dem jeweils letzten Reel um. Tag-Zähler steigt nur bei Teil 1.

## Grenzen
- Nichts Politisch-Reales, keine echten Staaten verspotten, nichts Beleidigendes/Sexuelles umsetzen; solche Top-Kommentare überspringen → nächstbester.
- Kein echtes Geld, keine Werbung, keine Deals ohne Besitzer.
- Name/Bio/Profilbild nur im Browser auf dem Rechner des Besitzers.

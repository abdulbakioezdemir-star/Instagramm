# Stil-Referenz: „Kinetic Type auf den Beat“ (Vorbild vom 13.11.2026)

Diese Art von Edit gefällt dem Kunden. Bei neuen Reels zuerst hier nachsehen und
diesen Stil verwenden, wenn nichts anderes gewünscht ist.

Vorbild: Bildschirmaufnahme eines Reels von @yp.motionstudio (10,6 s, Hochformat).
Text: „we don't just edit — we create motion · art · impact · visuals · energy ·
precision · rhythm · vibes · graphics · transitions · ideas · feelings · repeat.“ → Loop zu „we“.

## Grundprinzip
**Ein Wort = ein Schlag.** Das ganze Video ist Typografie im Takt der Musik.
Kein Effekt ohne Beat, kein Beat ohne Bildwechsel.

## Text
- Fast nur **ein Wort pro Bild**, kleingeschrieben, Satzzeichen nur am Schluss („repeat.“).
- Schrift: sehr fette, geometrische Grotesk (Sora ExtraBold / Inter Display Black passt),
  enge Laufweite (−0,04 bis −0,06 em).
- Groß, mittig, ca. 15–25 % der Bildbreite hoch. Wichtige Wörter **riesig**
  (fast bildbreit, z. B. „don't“, „edit“).
- **Gestapelte Paare**: kleines Wort oben links bündig, darunter das große Wort
  („we / don't“, „just / edit“). Das kleine Wort steht zuerst allein, das große knallt auf dem nächsten Beat dazu.
- **Tipp-Effekt** bei schnellen Beats: Buchstaben erscheinen in Silben pro Schlag
  („re“ → „repe.“ → „repea“ → „repeat.“).
- Ein Wort mit **Pinsel-/Masken-Wisch** (Strich zieht über das Wort und deckt es auf, „create“).

## Übergänge
- **Harte Schnitte genau auf dem Beat**, keine Überblendungen.
- **Farbumkehr bei jedem Wechsel**: Weiß auf Schwarz ↔ Schwarz auf Weiß, abwechselnd.
- Wort kommt mit kurzer **horizontaler Bewegungsunschärfe** (2–3 Frames) und steht dann still.
- Gelegentlich **Größensprung**: dasselbe Wort springt auf dem Beat von normal auf riesig („we“ → „WE“).
- Kein Wackeln, kein Pumpen, keine Kamerafahrten.

## Hintergrund
- Reines Weiß oder reines Schwarz, flach.
- Feine **Staub-/Kornpartikel** (wenige helle oder dunkle Pünktchen), dazu ein leichter Verlauf zum Rand.
- Keine Bilder und keine Farben. Höchstens eine Akzentfarbe der Marke, sparsam.

## Ton
- Rhythmische Musik, sehr gleichmäßiger Puls, ca. **150–160 BPM** (Wechsel alle ~0,38 s).
  Gemessen bei 0,35 · 1,01 · 1,58 · 3,11 · 3,99 · 4,40 · 4,80 · 5,14 · 5,50 · 5,89 · 6,21 · 6,54 · 7,16 · 7,46 · 7,75 · 8,04 · 8,31 · 8,58 · 9,26 s.
- Klang: kurze, perkussive Synth-/Pluck-Stabs (Energie bei 0,8–1,3 kHz) plus weicher Kick (~250 Hz).
  Jeder Stab = ein Wort.
- Anfang ruhiger, die Abstände werden zum Ende hin kürzer (Beschleunigung, 0,6 s → 0,3 s).
- Keine Stimme. Der Text *ist* die Stimme.

## Aufbau
1. Intro mit zwei bis drei langsamen Beats (gestapelte Paare, Statement).
2. Hauptteil: schnelle Wort-Kaskade, jeder Beat ein Begriff, Farbe wechselt jedes Mal.
3. Schluss mit Tipp-Effekt auf dem letzten Wort, dann **Loop** zurück zum ersten Wort,
   damit das Reel endlos weiterläuft.
4. Länge 8–12 Sekunden.

## Umsetzung (HyperFrames)
- Beat-Raster mit `npx hyperframes beats <musik> --json`, Wortwechsel exakt auf `beatTimes`.
- Pro Wort ein Element, Sichtbarkeit per `tl.set` auf dem Beat (harte Schnitte),
  Hintergrund-Farbe per `tl.set` mitwechseln.
- Bewegungsunschärfe: `fromTo(x: ±60, filter: blur(8px)) → (x: 0, blur 0)` in 0,08 s.
- Tipp-Effekt: Wort in Silben-Spans, Spans nacheinander per `tl.set` einblenden.

---

# Stil-Referenz 2: „Kreatives Motion Design mit Leitmotiv“ (Vorbilder vom 14.11.2026)

Das ist dem Kunden **am wichtigsten**: Kreativität, ein roter Faden, Übergänge mit Sinn,
und Soundeffekte, die genau auf die Übergänge abgestimmt sind. Fünf Vorbilder:

| Vorbild | Länge | Kern |
|---|---|---|
| marq (Agentur) | 15 s | zentrierte Kinetic-Type, Creme ↔ Nachtblau, Bewegungsunschärfe, Tippen, Akzentfarbe, Logo am Ende |
| motionthekx | 13 s | hellgrau, kleine Schrift rollt verschwommen; Icon → Profilkarte → „Follow“ → Pille → Vollbild in Farbe |
| kreativvy (Editor gesucht) | 14 s | Geschichte: „Still looking for an editor?“ → Instagram-Logo → Suchleiste → Cursor klickt „+“ → „Apply“ → Formular → Häkchen „Project completed“ |
| aslanieditz | 12 s | eine **leuchtende Lichtkugel** fährt über den Text, löscht ihn und schreibt den nächsten; wird zu gelben Säulen, dann zum gelben Auto (Draufsicht) mit Driftspuren und großem Titel |
| zantenews („Can AI replace…“) | 17 s | Papier-Textur, Handgezeichnetes, ausgeschnittene bunte Buchstaben setzen sich zusammen; Lupe, Auge, Noten, Klaviertasten, Tinte, Papierflieger |

## 1. Leitmotiv statt Effekte
- **Ein Objekt trägt die Geschichte durchs ganze Video**: Lichtkugel, Cursor, Stift-Linie, Lupe, Funke.
  Es bewegt sich, und **aus ihm entsteht die nächste Szene**: die Kugel wird zu Säulen, die Säulen zum Auto,
  das Logo zur Suchleiste, die Suchleiste zum Knopf, der Knopf zum Formular, das Formular zum Häkchen.
- Übergänge haben einen **Grund im Bild**: Klick, Wischen der Kugel, eine Linie, die sich zum nächsten Bild zieht, eine Form, die sich verwandelt.
  Keine Übergänge ohne Motiv.

## 2. Sinn / Geschichte
- Jedes Reel erzählt **Problem → Suche → Lösung → Ergebnis** (oder Idee → Weg → Ziel) in 12–17 Sekunden.
- Text ist kurz, groß oder elegant klein, immer **zentriert**, und kommuniziert die Geschichte zusammen mit den Objekten.
- Das Ende greift den Anfang auf (Loop).

## 3. Übergangs-Repertoire
- **Form-Morph**: Icon → Pille → Karte → Vollbild, mit runden Ecken, weich und genau.
- **Licht-Wisch**: Ein leuchtendes Objekt fährt über den Text, dahinter erscheint der neue Text.
- **Match-Cut**: Ein Objekt in Szene A sitzt an derselben Stelle wie in Szene B (Kugel → Scheinwerfer).
- **Zusammensetzen**: Buchstaben fliegen verstreut herein und ordnen sich zum Wort.
- **UI-Interaktion**: Cursor, Klick, Hover-Zustand, Häkchen-Animation.
- **Kurze dramatische Pause**: 0,3–0,6 s fast Stille und Dunkel vor dem großen Reveal (Vorbild kreativvy bei 8 s).
- **Weiche Unschärfe** beim Kommen und Gehen, nie hart ruckelnd, nie Wackeln oder Pumpen.

## 4. Look
- Eine klare Welt pro Reel: sauberes Hell-UI, warmes Gelb-Schwarz, Papier mit Korn oder Neon-dunkel.
- Eine Akzentfarbe, viel Ruhe drumherum, feines Korn und Glow für Wertigkeit.

## 5. Sound (genauso wichtig wie das Bild)
- **Jeder Übergang hat seinen Klang**: Whoosh zur Bewegung, Klick beim Tippen, Pop beim Erscheinen,
  Riser vor dem Reveal, Impact/Bass-Drop beim Reveal, Glitzern/Shimmer bei Licht.
- Bei Aufzählungen bekommt jedes Objekt einen **melodischen Ton** (Marimba/Pluck), sodass eine kleine Melodie entsteht (Vorbild zantenews).
- Musik leise darunter; **vor dem Reveal kurz alles wegnehmen**, dann mit voller Wucht zurück.
- Soundeffekte exakt auf den Frame der Bewegung legen, mit 1–2 Frames Vorlauf für den Anschlag.

## Umsetzung
- Erst die **Geschichte und das Leitmotiv** festlegen, dann die Szenen als Verwandlungen des Motivs planen.
- Sound-Spur als **Liste von Ereignissen** (Zeit, Art) zusammen mit der Animation erzeugen, damit Bild und Ton gleich liegen.

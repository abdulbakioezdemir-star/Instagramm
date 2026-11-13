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

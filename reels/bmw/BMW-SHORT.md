# BMW Short – „Das Logo ist kein Propeller" (30 s, 9:16)

Format 1080×1920 · 24 fps · Shorts / Reels / TikTok · Voiceover Deutsch, ruhig und präzise (ca. 2,3 Wörter/s).

## 1. Struktur & Skript

| Zeit | Voiceover | Bild |
|---|---|---|
| 0–5 s | „Das BMW-Logo ist kein Propeller." (Pause) „Auch wenn es fast jeder glaubt." | Extreme Makro-Aufnahme des Emblems auf der Motorhaube, Golden Hour; ein Lichtstreif wandert über das Emaille. |
| 5–15 s | „Der Propeller-Mythos stammt aus einer BMW-Werbeanzeige von 1929. Gemeint sind die Farben Bayerns: Weiß und Blau. Angefangen hat BMW 1916 – mit Flugmotoren." | Historisch anmutender Propeller dreht im Gegenlicht über Alpenvorland, Match Cut auf ein weiß-blaues Rautenmuster; dann ein polierter Reihen-Flugmotor in einer Werkstatt mit Lichtstrahlen. |
| 15–25 s | „1923 kam das erste Motorrad, 1928 das erste Auto. Und seit 1933 trägt die Front ein Erkennungszeichen: die Niere." | Klassisches Motorrad im Gegenlicht auf einer Landstraße; Überblendung auf einen modernen BMW in der Abendsonne, langsame Fahrt auf die Niere. |
| 25–30 s | „Jetzt weißt du, was das Logo wirklich zeigt." | Kamera fährt von der Niere zurück auf das Emblem – gleiche Einstellung wie Sekunde 0 (nahtloser Loop). |

Untertitel: Inter Bold, weiß, Schlüsselwörter („kein Propeller", „1929", „1916", „Niere") in einem gedämpften BMW-Blau (#1C69D4) hervorheben, Text nur zwischen 168 und 1330 px Höhe.

### KI-Video-Prompts (Runway Gen-3 / Sora / Luma)
Alle Prompts mit Seitenverhältnis 9:16. Markenlogo und Niere können KI-Modelle verfälschen oder verweigern – sicherer: Emblem in der Nachbearbeitung einsetzen bzw. echtes Footage/Pressefotos mit Freigabe nutzen.

**0–5 s – Hook**
> Extreme macro shot of a circular enamel car emblem on a dark blue metallic hood, golden hour sunlight, a slow specular light sweep travels across the chrome ring, shallow depth of field, 100mm macro lens, fine metallic flakes visible, soft shadows, photorealistic, analog film grade, Kodak Vision3 250D look, subtle halation, 24fps, 180-degree shutter, slow push-in, no text.

**5–10 s – Mythos**
> Close-up of a vintage wooden aircraft propeller slowly spinning against a low golden sun above rolling Bavarian farmland, volumetric light rays through morning haze, backlit dust particles, anamorphic 50mm lens, oval bokeh, gentle lens flare, muted warm palette, photorealistic, cinematic film grain, slow dolly to the side.

> Match cut: macro shot of a white and blue diamond pattern woven fabric gently waving in soft wind, warm rim light, shallow depth of field, photorealistic, analog color grading.

**10–15 s – 1916**
> Polished vintage inline aircraft engine on a wooden workbench in an old brick workshop, shafts of golden light through tall industrial windows, volumetric haze, slow orbit around the engine, 35mm lens, brass and steel textures, deep warm shadows, photorealistic, 8k detail, analog film look.

**15–20 s – Motorrad & Auto**
> A classic 1920s black motorcycle parked on an empty country road at sunset, long shadows, backlit golden haze, low angle tracking shot moving slowly past the bike, anamorphic lens, soft contrast, photorealistic, Kodak film color science, fine grain.

**20–25 s – Die Niere**
> A modern dark blue luxury sedan parked on a coastal road at golden hour, slow dolly-in toward the front grille, reflections of the warm sky gliding over the paint, volumetric sun rays, anamorphic 40mm lens, shallow depth of field, photorealistic, premium automotive commercial look, analog grade, no text.

**25–30 s – Loop**
> Continuous slow pull from a car grille up to the circular emblem on the hood, ending in an extreme macro of the emblem identical to the opening frame, golden hour light sweep, photorealistic, 100mm macro, analog film grade, seamless loop.

Negativ-Prompt (wo unterstützt): `cartoon, CGI look, oversaturated, HDR, plastic reflections, warped logo, text, watermark, extra wheels, distorted geometry, jitter`.

## 2. Ästhetik-Guide
- **Licht:** Golden Hour als Hauptlicht (ca. 3.200–4.000 K), tief und seitlich, damit Karosserielinien als Lichtkanten lesbar werden. Dazu Gegenlicht als Kante (Rim Light) und leichter Dunst für volumetrische Strahlen. Lackflächen zeigen weiche, lange Reflexionen statt harter Hotspots.
- **Farbe:** warme Lichter (Bernstein, Champagner), Schatten leicht ins Petrol, Mitten neutral. Blau nur als Akzent (Lack, Raute, Untertitel-Wort). Sättigung eher zurückhaltend, keine Neonfarben.
- **Analoger Look:** Filmemulation in Richtung Kodak Vision3 250D/500T, sanfter Highlight-Roll-off, feines 35-mm-Korn (2–3 %), dezente Halation an Spitzlichtern, leichte Vignette (5–8 %). Kein Überschärfen, kein HDR, kein Teal-Orange-Preset.
- **Texturen:** Metallic-Flakes im Lack, gebürstetes Aluminium, Emaille, Leder, Messing am Flugmotor – immer im Streiflicht, damit die Oberfläche sichtbar wird.
- **Kamera & Bewegung:** 24 fps, 180°-Shutter, langsame Dolly- und Orbit-Fahrten (keine Drehs über 10°/s), Makro 100 mm für Details, anamorph 40–50 mm für Szenen. Ein Schnitt alle 2,5–4 s, Match Cuts über Formen (Propeller → Raute → Emblem).
- **Ton:** ruhiger Ambient-Score mit leisem Puls, ein einzelner tiefer Akzent bei „1916", Foley (Metall-Klick, Wind, Motorstart leise) nur wo im Bild verursacht; Musik unter der Stimme absenken.

## 3. Automatisierung
Dateien in `automation/`:
- `posts.csv` – Planungstabelle (Datei, Titel, Beschreibung, Hashtags, Plattformen, Zeitpunkt, Status).
- `publish.py posten` – lädt fällige Zeilen zu YouTube (Data API v3), Instagram (Graph API, Reels) und TikTok (Content Posting API) hoch und schreibt Status/IDs zurück.
- `publish.py antworten --video <ID>` – beantwortet die ersten Kommentare (Standard: 5) auf YouTube einmalig mit einem Fakt aus `fakten.txt`, mit Pause dazwischen.
- Zugangsdaten nur als Umgebungsvariablen (siehe Kopf von `publish.py`).

Hinweise:
- TikTok-Apps ohne Audit dürfen nur privat (`SELF_ONLY`) posten.
- Instagram lädt das Video per öffentlicher URL.
- Automatische Antworten sparsam halten: Massen- oder Copy-Paste-Antworten verstoßen gegen die Spam-Regeln der Plattformen.

### Blueprint für Make.com (ohne Code)
1. **Google Sheets – Watch Rows:** Tabelle mit denselben Spalten wie `posts.csv`. Filter: `status = geplant` und `veroeffentlichen_um ≤ jetzt`.
2. **Google Drive – Download a File:** das MP4 zur Zeile.
3. **Router** mit drei Zweigen:
   - **YouTube – Upload a Video:** Titel, Beschreibung und Hashtags, Kategorie „Autos & Fahrzeuge".
   - **Instagram for Business – Create a Reel Post:** Video-URL aus Drive (öffentlich freigegeben) und Caption.
   - **TikTok:** Modul oder HTTP-Aufruf der Content Posting API.
4. **Google Sheets – Update a Row:** Status `veroeffentlicht` und die IDs eintragen.
5. **Zweites Szenario (alle 15 min, 24 h lang):**
   - **YouTube – List Comments** für die neue Video-ID.
   - **Filter:** noch keine Antwort und nicht in der „beantwortet"-Spalte.
   - **Tools – Set Variable:** zufälliger Fakt aus einer Faktenliste.
   - **YouTube – Reply to a Comment.**
   - Maximal 5 Antworten pro Video.

### Hinweis zur Marke
Das ist redaktioneller Fan-/Info-Content. Nicht als offizielle BMW-Werbung ausgeben und keine Wortmarken-Claims („Freude am Fahren") nutzen. Logos nur zur Bezugnahme zeigen, nicht verfremdet.

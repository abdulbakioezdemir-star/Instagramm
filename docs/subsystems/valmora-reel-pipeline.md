---
title: Valmora-Reel-Pipeline (Rendern + Posten)
type: subsystem
created: 2026-11-10
updated: 2026-11-10
sources:
  - code: nation/pipeline/tag02.py
  - code: nation/pipeline/tag01.py
  - code: nation/pipeline/bauten.py
  - code: nation/pipeline/world.py
  - code: nation/pipeline/synth_body.py
  - code: pipeline/tts.py
  - code: nation/NATION.md
  - code: nation/state.json
  - code: nation/LEARNINGS.md
verified_at: 175f0eb
---

# Valmora-Reel-Pipeline

Die Nations-Serie „Valmora“ (Konto `@valmora.nation`, Windsor-Account `17841459168444268`) besteht aus
täglichen Reels, die vollständig per Python gerendert werden: Bilder mit PIL, Musik und Soundeffekte
synthetisch mit numpy/scipy, Stimme per edge-tts. Spielregeln und Zeitplan stehen in `nation/NATION.md`,
der aktuelle Spielstand in `nation/state.json`.

## Ablauf eines Tages

1. **Stimme**: Jede Sprechzeile (`l1` … `lN`, Text in `nation/pipeline/lines_tag02.tsv`) wird mit
   `pipeline/tts.py` erzeugt. Dabei entstehen lN.mp3 und lN.mp3.json mit Wort-Zeitstempeln.
   Stimme: `de-DE-FlorianMultilingualNeural`, Pitch `-4Hz`, Rate `+4%` (siehe `state.json`, Feld `stimme`).
2. **Timeline**: Das Skript dekodiert alle Zeilen, reiht sie mit kurzen Pausen (`gaps`,
   `nation/pipeline/tag02.py:31`) hintereinander und leitet daraus die Szenengrenzen `S` ab.
   Animationen hängen über `wt(zeile, wortindex)` (`nation/pipeline/tag02.py:45`) an einzelnen Wörtern.
3. **Audio**: Stimme, SFX und Musik (Funktionen aus `nation/pipeline/synth_body.py`, per `exec` geladen)
   werden einzeln geschrieben und per ffmpeg mit Sidechain-Ducking und loudnorm zu `mix.wav` gemischt.
4. **Bild**: `frame(tt)` zeichnet jedes Bild bei 1080×1920 und 30 fps, inklusive HUD (Tag / Staatskasse /
   Einwohner / Gebäude) und wortgenauer Untertitel. Die Welt ist ein Panorama mit 3600×1920 Pixeln und eine Karte
   (`nation/pipeline/world.py`); Bauten zeichnet `nation/pipeline/bauten.py`.
5. **Prüfen**: `PREVIEW=auto python3 tag02.py` (im Arbeitsordner) speichert Einzelbilder als `pv_*.png` (ohne Audio-Render) für
   einen Kontaktbogen. Danach rendert der Lauf ohne `PREVIEW` das fertige mp4 (~25 s Rechenzeit für ~49 s Video).
6. **Posten**: Das Video kommt nach `media/nation/valmora_tagNN.mp4` und wird auf den Branch `content` gepusht.
   Danach postet Windsor `create_video_post` (mit `share_to_feed: true`) per raw-GitHub-Link.
   Anschließend werden `state.json` und `LEARNINGS.md` aktualisiert.

## Neuen Tag bauen

`nation/pipeline/tag02.py` ist die aktuelle Vorlage. Kopiere sie für Tag N, passe `TAG`, `K_ALT, LIKES, KOSTEN`
(`nation/pipeline/tag02.py:17`), die Zeilen und die Wortindizes an. Wenn ein neuer Bau dazukommt, schreibe
ihn als Funktion in `nation/pipeline/bauten.py` und zeichne ihn in `scene_world` (`nation/pipeline/tag02.py:209`)
dauerhaft mit: Was einmal gebaut ist, bleibt in allen Folgen sichtbar (Regel aus `nation/NATION.md`).

## Fallen

> ⚠️ Die Skripte erwarten ihre Eingaben **im aktuellen Arbeitsordner**: `nation/pipeline/synth_body.py`, `nation/pipeline/world.py`,
> `nation/pipeline/bauten.py`, `panorama.jpg`, `logo_valmora.jpg` und die Stimm-Dateien lN.mp3 und lN.mp3.json. Die Schriften liegen dagegen unter dem
> festen Pfad `/home/claude/instagramm/pipeline/fonts/` (`nation/pipeline/tag02.py:12`). Rendere in einem
> separaten Arbeitsordner und kopiere nur die Ergebnisse zurück ins Repo.

> ⚠️ `nation/pipeline/synth_body.py` wird per `exec` geladen und nutzt `sosfilt`/`butter`/`fftconvolve`, importiert sie aber
> nicht selbst. Das aufrufende Skript muss `from scipy.signal import butter, sosfilt, fftconvolve` **vor** dem
> `exec` ausführen (`nation/pipeline/tag02.py:5`), sonst bricht der Lauf mit `NameError: sosfilt` ab.

> ⚠️ Die Wortindizes in `wt("lN", i)` hängen am genauen Text der Zeile. edge-tts zählt Zahlwörter und
> Bindestrich-Wörter als ein Wort. Wenn sich ein Satz ändert, muss man die Indizes neu prüfen
> (`python3 -c "import json;print([w[2] for w in json.load(open('l3.mp3.json'))])"`), sonst erscheinen Tafeln
> zum falschen Wort. Passiert ist das an Tag 2 bei `KASSE_UP` und `BUILD0` (`nation/pipeline/tag02.py:58`).

> ⚠️ Lange Zahlwörter („ZWEIHUNDERTEINS MINUS HUNDERTFÜNFZIG“) passen in Bungee auch bei Größe 48 nicht zu
> dritt in eine Zeile. `sub_groups` (`nation/pipeline/tag02.py:157`) bricht deshalb nach Breite statt
> stur nach 3 Wörtern um. `nation/pipeline/tag01.py` hat diesen Fix noch nicht: Nimm nicht `nation/pipeline/tag01.py` als Vorlage.

> ⚠️ Gebäude werden in **Bildschirm-Koordinaten bei `pan_view(2150)`** gezeichnet (Leuchtturm bei x=470,
> Basis y=1420; Steg ab x=600, y=1330). Bei einem anderen Kamera-Ausschnitt muss man die x-Position um
> `2150 - x` verschieben (`nation/pipeline/tag02.py:241`), sonst steht das Haus im Meer.

> ⚠️ `edge-tts` ist in einer frischen Cloud-Umgebung nicht installiert:
> `pip install edge-tts --break-system-packages`. Wegen des Agent-Proxys setzt `pipeline/tts.py:3` ein
> eigenes CA-Bundle (`~/.ccr/ca-bundle.crt`); ohne diese Zeile schlägt TLS fehl.

> ⚠️ Der Repo-Name ist `instagramm` (klein). Raw-Links funktionieren zwar mit beiden Schreibweisen, aber nimm
> im Caption-/Post-Link die echte Schreibweise und prüfe den Link vor dem Posten mit `curl` (Status 200,
> Größe stimmt).

> ⚠️ Die Staatskasse wird **nie frei erfunden**: Sie ist immer `1000 + alle Likes aller Reels − ausgaben_eur`
> (`nation/state.json`, Feld `staatskasse_formel`). „Entdeckungen“ dürfen deshalb kein Geld bringen.

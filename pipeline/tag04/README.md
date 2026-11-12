# Tag 4 „Zwilling“ – Teil 1 (12 Uhr) & Teil 2 (18 Uhr)

Abstimmung Tag 3 Teil 2: **B 5 : A 2** → Ahmed sagt Lena, er sei Emres Zwilling.
- Teil 1 (gepostet 2026-11-12 12:00, 32,4 s): Cold Open „Ich hab Lena gesagt, ich bin Emres Zwilling. Wir sehen uns null ähnlich.“ (Text „ICH HAB JETZT EINEN ZWILLING.“ ab 0 s)
  → 5:2-Karte + Zuschauer-Easter-Egg („mach dich hübsch“ – „Bruder… das war schon hübsch.“) → Videoanruf „Er hat die Muskeln gekriegt. Ich das WLAN-Passwort.“
  → Lena „Ihr seid Zwillinge? Voll süß! Schick mir ein Foto von euch beiden. Jetzt.“ (FOTO. JETZT.) → Chat mit Emre, der nur Daumen hoch schickt → „TEIL 2 · HEUTE 18 UHR“.
- Teil 2 (18 Uhr, fertig getestet, 31,8 s): Hook-Text „ICH HAB MICH SELBST GEKLONT.“ → Panorama-Trick (links stehen, rennen, rechts stehen)
  → Foto mit 3 Armen, Lena „warum hat dein Bruder drei Arme?“ → „Er… geht halt viel ins Fitnessstudio.“ (ARMTAG. JEDEN TAG.)
  → Lena „Voll süß. Dann ruf ihn doch dazu. Jetzt. Wir drei.“ (ZU DRITT?!) → Poll A = Echten Emre anrufen, B = Ahmed spielt beide → „TAG 5 – MORGEN 12 UHR“.

## Rendern (18-Uhr-Lauf)
Setup wie in `pipeline/tag02/README.md` (pip edge-tts skia-python, draw.py/scenes.py/audio.py/mix.sh/tts.py/fonts nach /home/claude, Dummy-timeline.json, /home/claude/tag2 inkl. TTS-Schleife).
Repo muss unter `/home/claude/instagramm` liegen (Branch content).
```bash
cd /home/claude/instagramm/pipeline/tag04
python3 tag04.py 2 tts      # falls eine Zeile mit ffmpeg-Fehler abbricht (edge-tts-Aussetzer): einfach nochmal
python3 tag04.py 2 preview 0.5 4 7 10.5 13 16 19 21 24 28 31   # -> /home/claude/tag04_work/teil2/prev.png
python3 tag04.py 2 all /home/claude/instagramm/media/glowup/tag04_teil2.mp4
```
Caption-Vorschlag Teil 2:
Tag 4 · Teil 2/2 / Ahmed fälscht ein Zwillingsfoto mit dem Panorama-Trick – und sein „Bruder“ hat 3 Arme 💪💪💪 / A = Den echten Emre anrufen / B = Ahmed spielt einfach beide / Schreibt A oder B – die Mehrheit entscheidet Tag 5 (morgen 12 Uhr)! / Schick das deinem Freund, der jedes Foto 20× neu macht 😂 / #ahmedglowup #animation #comedy #dating #reels

Hinweis: Whisper erkennt Seraphinas kurzes „Süß!“ als „Sass“ → immer „Voll süß“ schreiben.

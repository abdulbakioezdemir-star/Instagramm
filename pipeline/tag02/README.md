# Tag 2 „Beides“ – Teil 1 (12 Uhr) & Teil 2 (18 Uhr)

Abstimmung Tag 1: A=2, B=2 → Unentschieden → Ahmed macht BEIDES.
- Teil 1 (gepostet 2026-11-10 12:00): Cold Open kalte Dusche → „Zwei sagen A, zwei sagen B“ → Dönerbude, gefeuert → Dusche, Stromrechnung → Lena-Videoanruf → Cliffhanger „ANNEHMEN?“ + „Teil 2 heute 18 Uhr“.
- Teil 2 (18 Uhr): „Vorhin bei Ahmed…“ → Ahmed friert, Handy klingelt (Erdbeben-Gag) → Lena: „Geh ran!“ → A/B-Abstimmung: A = Emre geht ran, B = Kamera „kaputt“ → „Tag 3 – morgen 12 Uhr“.

## Rendern (18-Uhr-Lauf)
```bash
# Laufzeit-Layout (Pfade sind in draw.py/scenes.py/tag2.py fest verdrahtet)
cd /home/claude && P=instagramm/pipeline
pip install edge-tts skia-python --break-system-packages -q
cp $P/draw.py $P/scenes.py $P/audio.py $P/mix.sh $P/tts.py . && cp -r $P/fonts .
echo '{"mouth":[0],"ev":{},"t1":"","scenes":[],"lines":[],"total":1}' > timeline.json
mkdir -p tag2 && cp $P/tag2/* tag2/ && cd tag2 && while IFS=$'\t' read i w txt; do v=de-DE-FlorianMultilingualNeural; r=+7%; [ "$w" = L ] && v=de-DE-SeraphinaMultilingualNeural && r=+0%; python3 /home/claude/tts.py "$txt" $v $i.mp3 +0Hz $r </dev/null; ffmpeg -nostdin -v error -y -i $i.mp3 -ar 48000 -ac 1 $i.wav; done < lines.tsv
cd /home/claude/instagramm/pipeline/tag02
python3 tag02.py 2 tts                        # Stimmen erzeugen + Timeline
python3 tag02.py 2 preview 0.5 5 12 20 26 33  # Kontaktbogen -> /home/claude/tag02_work/teil2/prev.png
python3 tag02.py 2 all /home/claude/instagramm/media/glowup/tag02_teil2.mp4   # ~1,5 min
```
Stimmen (Spektral-Abgleich mit tag02_beides_v2.mp4): Ahmed = de-DE-FlorianMultilingualNeural +0Hz +7 %,
Lena = de-DE-SeraphinaMultilingualNeural +0Hz +0 %, Dönermann = de-DE-ConradNeural +0Hz +0 %.
Untertitel-Anzeige-Texte (Zahlen als Ziffern usw.) in `disp.tsv`.

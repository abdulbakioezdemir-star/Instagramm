#!/bin/bash
set -e
cd "$(dirname "$0")/.."
mix() { # version music start gain extra_crackle
  local cr="" ; local ins=2 ; local lab="[duck][vo]"
  if [ "$5" = "1" ]; then cr="-i audio/crackle.wav"; fi
  local fc="[1:a]afade=t=in:d=0.3,afade=t=out:st=16.5:d=1.5,volume=$4dB[m0];[2:a]highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=150,volume=2dB,apad,asplit=2[vo][sc];[m0][sc]sidechaincompress=threshold=0.04:ratio=3.5:attack=15:release=300:makeup=1[duck]"
  if [ "$5" = "1" ]; then fc="$fc;[3:a]volume=0.8[cr]"; lab="[duck][vo][cr]"; ins=3; fi
  ffmpeg -nostdin -v error -y -i build/$1.mp4 -ss $3 -t 18 -i "$2" -i audio/chris.mp3 $cr -filter_complex "$fc;${lab}amix=inputs=$ins:normalize=0,atrim=0:18,loudnorm=I=-14:TP=-1.5:LRA=9[a]" \
    -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart kevin-$1.mp4
  echo "$1 $(ffmpeg -nostdin -nostats -i kevin-$1.mp4 -af ebur128 -f null - 2>&1 | grep 'I:' | tail -1)"
}
for v in A B C D; do python3 tools/refbuild.py $v >/dev/null; npx --yes hyperframes@0.9.27 render --quality delivery --workers 2 -o build/$v.mp4 2>&1 | grep -E "MB ·" || true; done
mix A audio/music.wav 0 -1 0
mix B audio/rudenko-peace.mp3 63.8 0 0
mix C audio/synthwave.wav 0 -1 0
mix D audio/rudenko-inhale2.mp3 64.68 0 1

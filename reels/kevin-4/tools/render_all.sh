#!/bin/bash
# renders the four cuts and mixes voice + music for each
set -e
cd "$(dirname "$0")/.."
mix() { # $1 version  $2 music file  $3 media start  $4 music gain dB  $5 boom(0/1)
  local extra="" ; local n=2
  if [ "$5" = "1" ]; then extra="-i ../kevin-potenzial/sfx/boom.wav"; fi
  local boomf="" ; local inputs=2
  if [ "$5" = "1" ]; then boomf=";[3:a]adelay=8200|8200,volume=0.45,apad[bm]"; inputs=3; fi
  local mixin="[duck][vo]"; [ "$5" = "1" ] && mixin="[duck][vo][bm]"
  ffmpeg -nostdin -v error -y -i build/$1.mp4 -ss $3 -t 18 -i "$2" -i audio/chris.mp3 $extra -filter_complex \
   "[1:a]afade=t=in:d=0.3,afade=t=out:st=16.5:d=1.5,volume=$4dB[m0];[2:a]highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=150,volume=2dB,apad,asplit=2[vo][sc];[m0][sc]sidechaincompress=threshold=0.04:ratio=3.5:attack=15:release=300:makeup=1[duck]$boomf;${mixin}amix=inputs=$inputs:normalize=0,atrim=0:18,loudnorm=I=-14:TP=-1.5:LRA=9[a]" \
   -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart kevin-$1.mp4
  echo "$1 $(ffmpeg -nostdin -nostats -i kevin-$1.mp4 -af ebur128 -f null - 2>&1 | grep 'I:' | tail -1)"
}
for v in v1 v2 v3 v4; do
  python3 tools/build4.py $v >/dev/null
  npx --yes hyperframes@0.9.27 render --quality delivery --workers 2 -o build/$v.mp4 2>&1 | grep -E "MB ·" || true
done
mix v1 audio/engel-mechanical-heart.mp3 8.75 0 0
mix v2 audio/music.wav 0 -1 0
mix v3 audio/onni-goodnight.mp3 6.32 -4 0
mix v4 audio/zp-return-king.mp3 62.85 -1 1

#!/usr/bin/env bash
# Macht den Ton einer Datei sichtbar: Spektrogramm + Wellenform als PNG.
# Nutzung: tools/ohren/spektrum.sh video.mp4 ausgabe-ordner
set -euo pipefail
in="$1"; out="${2:-.}"; mkdir -p "$out"; base="$(basename "${in%.*}")"
ffmpeg -y -v error -i "$in" -lavfi "showspectrumpic=s=1600x500:legend=1:scale=log:fscale=log:color=intensity:stop=12000,format=rgb24" "$out/$base-spektrum.png"
ffmpeg -y -v error -i "$in" -lavfi "showwavespic=s=1600x200:colors=#ffc94d" "$out/$base-welle.png"
echo "$out/$base-spektrum.png"; echo "$out/$base-welle.png"

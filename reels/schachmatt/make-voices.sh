#!/usr/bin/env bash
# Erzeugt die deutschen Stimmen für "Schachmatt" auf deinem Laptop und pusht sie.
# Voraussetzung: heygen CLI installiert + "npx hyperframes auth login" erledigt.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/voice
M=d284344a1ba04039bdfdede36a319f32   # Erzähler: Mordecai
F=be8d7bf8ce774bda8b6dd04541fb8623   # Kollege: Florian
N=194c5c7896e849139df58b34b05b6a7c   # Kollegin: Nele
C=cd74981dc65345689233cc3b694faff7   # Chef: Ilya
line() {
  local id="$1" voice="$2" text="$3"
  echo "→ $id: $text"
  out=$(npx hyperframes media-use resolve --type voice --voice-id "$voice" --intent "$text" --project . 2>&1 | tee /dev/stderr | grep -E "^resolved" | tail -1)
  path=$(echo "$out" | sed -E 's/^resolved [^ ]+ → ([^ ]+).*/\1/')
  [ -f "$path" ] || { echo "Fehler bei $id"; exit 1; }
  cp "$path" "assets/voice/$id.${path##*.}"
}
line n1 $M "Er hatte alles."
line n2 $M "Dann verlor er alles."
line k1 $F "Das ist echt der Ex-Chef? Krass."
line k2 $N "Opa, der Drucker ist da drüben."
line k3 $F "Nichts geht mehr! Alles ist down!"
line n3 $M "Aber sein Wissen konnte ihm keiner nehmen."
line k4 $N "Wer… war das?"
line c1 $C "Ab morgen leitest du das Team."
line n4 $M "Unterschätz nie jemanden, der von unten kommt."
git add assets/voice
git commit -m "Add German voice lines for Schachmatt"
git push
echo "Fertig! Sag Claude Bescheid."

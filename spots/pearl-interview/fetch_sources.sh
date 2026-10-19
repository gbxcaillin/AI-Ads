#!/usr/bin/env bash
# Pull only the seconds the cut needs from the Drive files (each is 3 to 4 GB).
# ffmpeg cannot reach Drive through the session proxy, so drive_relay.py serves the files on
# localhost and fetches 8 MB chunks with curl, once each, into a cache. Drive's anonymous
# download quota is small: pull narrow windows, never whole files.
# Run from the repo root: bash spots/pearl-interview/fetch_sources.sh
set -euo pipefail
D=spots/pearl-interview; SRC=$D/src; CACHE=${CACHE:-/tmp/pearl-drive-cache}
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
SW=1yZgHVlulT88qSVTklsz-E6dQYJJQnAH8; MIC=1aNlVECq42vY_F9XUuMJeThcaDqXc5eER; MIC_OFF=50.66
mkdir -p "$SRC"
python3 -I $D/drive_relay.py 8765 "$CACHE" & RELAY=$!; trap 'kill $RELAY' EXIT; sleep 1
R=http://127.0.0.1:8765
# window  start(switched s)  duration
WINDOWS="A 529.9 15.5
B 947.6 17.0
C 1100.4 11.5"
echo '{' > $SRC/windows.json; first=1
while read -r n s d; do
  "$FF" -v error -y -ss "$s" -t "$d" -i "$R/$SW.mp4" -map 0:v -map 0:a -c copy "$SRC/$n-sw.mp4"
  ms=$(python3 -c "print($s+$MIC_OFF)")
  "$FF" -v error -y -ss "$ms" -t "$d" -i "$R/$MIC.wav" -c:a pcm_s24le "$SRC/$n-mic.wav" || echo "mic window $n failed; the build falls back to the switched audio"
  [ $first = 1 ] || echo ',' >> $SRC/windows.json; first=0
  printf '"%s": {"start": %s, "dur": %s}' "$n" "$s" "$d" >> $SRC/windows.json
  echo "window $n ok"
done <<< "$WINDOWS"
echo '}' >> $SRC/windows.json
ls -la "$SRC"

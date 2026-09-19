#!/usr/bin/env bash
# Install what the ai-commercial skill needs in a fresh session.
#   scripts/setup.sh          light: ffmpeg only (fast, runs at session start)
#   scripts/setup.sh --full   plus faster-whisper and playwright-core for narration splitting and screen captures
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1; then
  python3 -m pip install -q imageio-ffmpeg
  FF=$(python3 -c "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())")
  echo "ffmpeg: $FF (not on PATH; the skill scripts find it through imageio_ffmpeg)"
else
  echo "ffmpeg: $(command -v ffmpeg)"
fi

if [[ "${1:-}" == "--full" ]]; then
  python3 -m pip install -q -r requirements.txt
  if ! npm ls -g playwright-core >/dev/null 2>&1; then
    npm install -g playwright-core
  fi
  echo "chromium: ${CHROMIUM_PATH:-/opt/pw-browsers/chromium}"
fi

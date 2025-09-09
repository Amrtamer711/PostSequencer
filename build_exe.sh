#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name "ArtworkSequencer" \
  billboard_sequencer.py

echo "Built executable at ./dist/ArtworkSequencer" 
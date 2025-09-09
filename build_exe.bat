@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name ArtworkSequencer ^
  billboard_sequencer.py

echo Built executable at .\dist\ArtworkSequencer.exe
pause 
## Artwork Sequencer — Build and Usage (macOS)

### What’s included now
- Enter-only progression: press Enter to switch to Side 2 and press Enter again to finish.
- Clean end screen: tidy table, auto-sized window, centered buttons.
- Outputs saved to a stable folder: `~/Documents/Artwork Sequencer Outputs/` (images and reports).

### Build options on macOS

#### Option A: Build a .app bundle (recommended for sharing)
```bash
cd "/Users/amr/Documents/Pixel Finder"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name "ArtworkSequencer" billboard_sequencer.py
```
- Result: `dist/ArtworkSequencer.app`
- Double‑click to run or: `open "dist/ArtworkSequencer.app"`

#### Option B: Build a single-file GUI executable
Using the provided script:
```bash
cd "/Users/amr/Documents/Pixel Finder"
chmod +x build_exe.sh
./build_exe.sh
```
- Result: `dist/ArtworkSequencer` (single file, windowed)
- Double‑click to run or: `./dist/ArtworkSequencer`

Note: Quoted paths are important because the folder name contains a space ("Pixel Finder"). If you prefer, `cd` into the folder first, then run commands without long paths.

### Distributing to a colleague on Mac
- If you built the `.app`: zip it before sending so the bundle stays intact.
  - Finder: Right‑click `ArtworkSequencer.app` → Compress.
  - Terminal: `cd dist && zip -r ArtworkSequencer-mac.zip ArtworkSequencer.app`
- If you built the single file: you can zip and send `dist/ArtworkSequencer`.

#### First‑run Gatekeeper notes
- If macOS blocks the app: Right‑click the app → Open → Open.
- Or System Settings → Privacy & Security → “ArtworkSequencer was blocked” → Allow Anyway → Open.
- If “is damaged and can’t be opened” appears, remove quarantine then open:
```bash
xattr -dr com.apple.quarantine "/path/to/ArtworkSequencer.app"
open "/path/to/ArtworkSequencer.app"
```

#### Chip compatibility
- Build on the same chip architecture as the target Mac (Apple Silicon vs Intel) to avoid “bad CPU type” errors.

### How to use the app
1. Launch the app.
2. Choose road type (Single Way or Two Way) and the number of unique Artworks.
3. Click START, pick a road image, then click lamp posts in order.
4. Controls:
   - Enter: switch from Side 1 to Side 2 (two-way), then Enter again to finish.
   - Clicking: places the next Artwork number with a dot for visual feedback.
5. End screen:
   - Auto-sized, clean table view of Artwork counts.
   - Buttons centered under the table: Save Report, Done.
6. Files saved to `~/Documents/Artwork Sequencer Outputs/`:
   - `Artwork_sequence_YYYYMMDD_HHMMSS.jpg` (image with numbers only)
   - `Artwork_report_YYYYMMDD_HHMMSS.txt` (text report)

### Windows (optional)
A Windows build script is included if needed on a PC:
```bat
build_exe.bat
```
- Produces `dist/ArtworkSequencer.exe`.
- Outputs will save to the user’s `Documents/Artwork Sequencer Outputs/` folder. 
# CozyCorner

A cozy, aesthetic, autonomous desktop widget for your home screen.

## Features
- **Aesthetic**: Pixel-art cottage background with a warm vibe.
- **Companions**: A cute cat that sleeps, sits, and cleans itself.
- **Atmosphere**: Autonomous glowing fireflies wondering around.
- **Interactive**: 
  - **Drag** anywhere to move.
  - **Resize** using the bottom-right corner.

## Usage
Simply run the executable:
`cozy_widget.exe`

## Development
To run from source:
1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python cozy_widget.py
   ```

## Compiling
To build the `.exe` yourself:
```bash
pyinstaller --onefile --noconsole --add-data "assets;assets" cozy_widget.py
```

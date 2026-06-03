# Warframe Relic Overlay

**Warframe Relic Overlay** is a desktop companion app for Warframe that listens to the game's EE.log, captures your screen during relic reward selection, uses OCR to recognize item names, and displays an overlay with their current market value and ducat worth — right on top of your game, without interrupting your flow.

--

## ✨ Features

- Automatically screenshots the game when a relic reward appears  
- Uses Tesseract OCR to extract item names from screen regions  
- Fetches real-time Platinum prices and ducat values via Warframe APIs  
- Displays compact overlay windows that appear above the game  
- Fuzzy matching ensures reliable recognition even with OCR errors  
- Global hotkeys:
  - `Home` — update the local item database  
  - `PageDown` — cleanly exit the app  

--

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and ensure it’s available in your system PATH  
   *(Windows: `choco install tesseract` or use the official installer)*

3. Copy `.env.example` to `.env` and update the values based on your system

4. Launch the app:

```bash
python main.py
```

5. Press `Home` to update the item database, and you're ready to farm relics!

--

## .env Configuration

```env
# Path to your EE.log file
EE_LOG_PATH=/absolute/path/to/EE.log

# SQLite database filename
DB_NAME=items.db

# Debug mode: enables screenshot saving
DEBUG=True

# Path to YOLO model
MODEL_PATH=best.pt
```

--

## WIP / Known Limitations

- Inventory scanning is being integrated — will show extra info in the overlay
- Future overlay features planned:
  - Real overlay with info
  - Rotation tracking

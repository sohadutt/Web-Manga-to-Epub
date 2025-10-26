#!/bin/bash
set -e  # Exit on any error

# --- CONFIG ---
VENV_DIR=".venv"
PACKAGE_NAME="reigokai-scraper"

echo "🚀 Starting local setup for $PACKAGE_NAME..."

# --- 1️⃣ Create virtual environment if missing ---
if [ ! -d "$VENV_DIR" ]; then
    echo "🟢 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists, skipping..."
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# --- 2️⃣ Upgrade pip ---
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# --- 3️⃣ Install scraper dependencies and local package ---
echo "📦 Installing $PACKAGE_NAME locally (editable mode)..."
pip install --upgrade reigokai-scraper
echo "📦 Installing additional dependencies..."
pip install requests beautifulsoup4 tqdm ebooklib fpdf python-dotenv lxml

# --- 4️⃣ Download font if missing ---
PYTHON_ASSETS_SCRIPT=$(cat <<'END'
import os
from pathlib import Path
import requests

assets_dir = Path(__file__).parent / "reigokai_scraper" / "assets"
assets_dir.mkdir(exist_ok=True)

font_file = assets_dir / "DejaVuSans.ttf"
if not font_file.exists():
    print("📦 Downloading DejaVuSans.ttf...")
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    font_file.write_bytes(response.content)
    print("✅ Font downloaded.")
else:
    print("✅ Font already exists, skipping...")
END
)

python3 -c "$PYTHON_ASSETS_SCRIPT"

# --- 5️⃣ Run scraper ---
echo "🚀 Running $PACKAGE_NAME..."
reigokai-scraper

echo "🎉 Setup complete!"

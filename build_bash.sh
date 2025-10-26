#!/bin/bash
set -e  # Exit on any error


VENV_DIR=".venv"
PACKAGE_NAME="reigokai-scraper"

echo "🚀 Starting local setup for $PACKAGE_NAME..."


if [ ! -d "$VENV_DIR" ]; then
    echo "🟢 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists, skipping..."
fi


source "$VENV_DIR/bin/activate"


echo "⬆️ Upgrading pip..."
pip install --upgrade pip


echo "📦 Installing $PACKAGE_NAME locally (editable mode)..."
pip install --upgrade reigokai-scraper
echo "📦 Installing additional dependencies..."
pip install requests beautifulsoup4 tqdm ebooklib fpdf python-dotenv lxml


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

echo "🚀 Running $PACKAGE_NAME..."
reigokai-scraper

echo "🎉 Setup complete!"

#!/bin/bash
set -e

VENV_DIR="venv"
PACKAGE_NAME="reigokai-scraper"

echo "🚀 Starting local setup for $PACKAGE_NAME..."

# 1️⃣ Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "🟢 Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists, skipping..."
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# 2️⃣ Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 3️⃣ Install local package (editable mode)
echo "📦 Installing $PACKAGE_NAME locally..."
pip install --upgrade --editable .

# 4️⃣ Download assets/fonts if missing
ASSETS_DIR="./assets"
FONT_FILE="$ASSETS_DIR/DejaVuSans.ttf"
mkdir -p "$ASSETS_DIR"

if [ ! -f "$FONT_FILE" ]; then
    echo "📦 Downloading DejaVuSans.ttf..."
    curl -L -o "$FONT_FILE" "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
    echo "✅ Font downloaded to $FONT_FILE"
else
    echo "✅ Font already exists, skipping..."
fi

# 5️⃣ Run scraper
echo "🚀 Running $PACKAGE_NAME..."
reigokai-scraper

echo "🎉 Done!"

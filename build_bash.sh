#!/bin/bash
set -e

# --- CONFIG ---
VENV_DIR="venv"
PACKAGE_NAME="reigokai-scraper"
REPO_ZIP_URL="https://github.com/sohadutt/Web-Manga-to-Epub/archive/refs/heads/main.zip"
REPO_DIR="Web-Manga-to-Epub-main"
ASSETS_DIR="./assets"
FONT_FILE="$ASSETS_DIR/DejaVuSans.ttf"

echo "🚀 Starting setup for $PACKAGE_NAME..."

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
pip install --upgrade pip setuptools wheel

# 3️⃣ Download repo ZIP if missing
if [ ! -d "$REPO_DIR" ]; then
    echo "📥 Downloading $PACKAGE_NAME from GitHub..."
    curl -L -o "${PACKAGE_NAME}.zip" "$REPO_ZIP_URL"
    echo "📦 Extracting ZIP..."
    unzip -q "${PACKAGE_NAME}.zip"
    rm "${PACKAGE_NAME}.zip"
else
    echo "✅ Repo already exists, skipping download..."
fi

# 4️⃣ Install Python package and dependencies
echo "📦 Installing dependencies and $PACKAGE_NAME locally..."
pip install --upgrade --editable "$REPO_DIR"

# 5️⃣ Download assets/fonts if missing
mkdir -p "$ASSETS_DIR"
if [ ! -f "$FONT_FILE" ]; then
    echo "📦 Downloading DejaVuSans.ttf..."
    curl -L -o "$FONT_FILE" "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
    echo "✅ Font downloaded to $FONT_FILE"
else
    echo "✅ Font already exists, skipping..."
fi

# 6️⃣ Run scraper directly via Python
echo "🚀 Running $PACKAGE_NAME..."
python3 -m reigokai_scraper.__main__

echo "🎉 Setup and execution complete!"

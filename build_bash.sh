#!/usr/bin/env bash
set -e

VENV_DIR="venv"
PACKAGE_NAME="reigokai-scraper"
REPO_ZIP_URL="https://github.com/sohadutt/Web-Manga-to-Epub/archive/refs/heads/main.zip"
REPO_DIR="Web-Manga-to-Epub-main/reigokai-scraper"
ASSETS_DIR="./assets"
FONT_FILE="$ASSETS_DIR/DejaVuSans.ttf"
FONT_URL="https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"

echo "🚀 Starting setup for $PACKAGE_NAME..."

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OS" == "Windows_NT" ]]; then
    OS_NAME="Windows"
    PYTHON_CMD="python"
    ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_NAME="macOS"
    PYTHON_CMD="python3"
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
else
    OS_NAME="Linux"
    PYTHON_CMD="python3"
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
fi

echo "💻 Detected OS: $OS_NAME"

if [ ! -d "$VENV_DIR" ]; then
    echo "🟢 Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists."
fi

if [ -f "$ACTIVATE_PATH" ]; then
    source "$ACTIVATE_PATH"
else
    echo "❌ ERROR: Could not find activation script at $ACTIVATE_PATH"
    exit 1
fi

echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

if [ ! -d "$REPO_DIR" ]; then
    echo "📥 Downloading $PACKAGE_NAME..."
    curl -L -o "${PACKAGE_NAME}.zip" "$REPO_ZIP_URL"
    unzip -q "${PACKAGE_NAME}.zip"
    rm "${PACKAGE_NAME}.zip"
else
    echo "✅ Repository already exists."
fi

echo "📦 Installing dependencies..."
pip install --upgrade requests beautifulsoup4 tqdm ebooklib fpdf python-dotenv lxml

mkdir -p "$ASSETS_DIR"
if [ ! -f "$FONT_FILE" ]; then
    echo "📦 Downloading DejaVuSans.ttf..."
    curl -L -o "$FONT_FILE" "$FONT_URL"
else
    echo "✅ Font already exists."
fi

echo "🚀 Running $PACKAGE_NAME..."
$PYTHON_CMD "$REPO_DIR/__main__.py"

echo "🎉 Setup and execution complete!"
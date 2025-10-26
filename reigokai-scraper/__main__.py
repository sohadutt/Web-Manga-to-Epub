import os
import sys
import requests
from pathlib import Path
import zipfile

def extract_assets():
    """Extract bundled assets.zip if present."""
    base_dir = Path(__file__).parent
    zip_path = base_dir / "assets.zip"
    extract_dir = base_dir / "assets"

    if zip_path.exists() and not extract_dir.exists():
        print("📂 Extracting assets.zip...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        print("✅ Assets extracted.")
    elif extract_dir.exists():
        # Assets already extracted
        pass
    else:
        print("⚠️ No assets.zip found (continuing...)")
    return extract_dir

def ensure_font():
    """Ensure DejaVuSans.ttf exists or download it automatically."""
    assets_dir = Path(__file__).parent / "assets"
    font_path = assets_dir / "DejaVuSans.ttf"
    assets_dir.mkdir(exist_ok=True)

    if not font_path.exists():
        print("📦 Downloading DejaVuSans.ttf...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            font_path.write_bytes(response.content)
            print("✅ Font downloaded successfully.")
        except Exception as e:
            print(f"❌ Failed to download font: {e}")
            sys.exit(1)

    return font_path

def main():
    """Main entry point for the packaged app."""
    print("🚀 Starting Reigokai Scraper...")

    # Ensure assets and fonts
    extract_assets()
    font_file = ensure_font()

    # Attempt to import scraper
    try:
        # Import scraper from local package
        sys.path.insert(0, str(Path(__file__).parent))
        import scraper

        # Call run() with font file path
        # Make sure scraper.run(font_file) accepts 1 argument
        scraper.run(str(font_file))

    except ImportError as e:
        print(f"❌ Could not import scraper module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

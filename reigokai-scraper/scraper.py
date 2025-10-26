import os
import requests
import json
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm import tqdm
from ebooklib import epub
from fpdf import FPDF
from pathlib import Path

def ensure_font():
    """Download DejaVuSans.ttf if missing and return path."""
    font_path = Path(__file__).parent / "assets" / "DejaVuSans.ttf"
    font_path.parent.mkdir(exist_ok=True)
    if not font_path.exists():
        print("📦 Downloading DejaVuSans.ttf...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            font_path.write_bytes(response.content)
            print("✅ Font downloaded.")
        except Exception as e:
            print(f"❌ Failed to download font: {e}")
            raise
    return str(font_path)


def run():
    """Main entry point for the Reigokai scraper."""
    load_dotenv()

    # --- User input ---
    DEFAULT_CATEGORY_ID = "33"
    CATEGORY_ID = input(f"Enter category ID (default {DEFAULT_CATEGORY_ID}): ") or DEFAULT_CATEGORY_ID
    print(f"📌 Using Category ID: {CATEGORY_ID}")

    CF_CLEARANCE = os.getenv("CF_CLEARANCE")
    if not CF_CLEARANCE:
        raise ValueError("⚠️ CF_CLEARANCE environment variable not set. Add it to your .env file.")

    BASE_URL = "https://reigokaitranslations.com/wp-json/wp/v2/posts"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json",
        "Referer": "https://reigokaitranslations.com/",
        "Cookie": f"cf_clearance={CF_CLEARANCE}"
    }

    # --- Helpers ---
    def get_category_name(category_id):
        url = f"{BASE_URL.replace('posts','categories')}/{category_id}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("name", f"category_{category_id}").replace(" ", "_")
        except:
            pass
        return f"category_{category_id}"

    def clean_html(raw_html):
        soup = BeautifulSoup(raw_html, "lxml")
        for selector in [".sharedaddy", ".post-navigation", ".entry-footer", "script", "style"]:
            for el in soup.select(selector):
                el.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n\n".join(lines)

    def clean_story_content(raw_text):
        raw_text = re.sub(r"TL:.*\n", "", raw_text)
        raw_text = re.sub(r"Support my translations.*", "", raw_text, flags=re.IGNORECASE)
        raw_text = re.sub(r"(Next Chapter\s*\n)+", "", raw_text)
        raw_text = re.sub(r"(Previous Chapter\s*\n)+", "", raw_text)
        raw_text = re.sub(r"Not a Chapter:.*\n", "", raw_text)
        raw_text = re.sub(r"Author:.*\n", "", raw_text)
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)
        return raw_text.strip()

    def fetch_post_content(url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            content_div = soup.find("div", class_="entry-content")
            return {
                "title": (soup.find("h1", class_="entry-title") or "").get_text(strip=True) or "No Title",
                "content": clean_story_content(clean_html(str(content_div))) if content_div else "No Content",
                "date": (soup.find("time", class_="entry-date") or {}).get("datetime", "No Date"),
                "url": url
            }
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None

    # --- Setup files/folders ---
    CATEGORY_NAME = get_category_name(CATEGORY_ID)
    POSTS_JSON_FILE = f"{CATEGORY_NAME}_posts.json"
    CONTENT_JSON_FILE = f"{CATEGORY_NAME}_content.json"
    OUTPUT_DIR = f"{CATEGORY_NAME}_ebook"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Fetch posts ---
    all_posts = []
    if os.path.exists(POSTS_JSON_FILE):
        with open(POSTS_JSON_FILE, "r", encoding="utf-8") as f:
            all_posts = json.load(f)
    else:
        page = 1
        print("🌐 Fetching posts from API...")
        with tqdm(desc="API Pages", unit="page") as pbar:
            while True:
                url = f"{BASE_URL}?categories={CATEGORY_ID}&per_page=100&page={page}"
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    break
                data = response.json()
                if not data:
                    break
                all_posts.extend([{"title": p["title"]["rendered"], "url": p["link"], "date": p["date"]} for p in data])
                page += 1
                pbar.update(1)
        with open(POSTS_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=2)

    all_posts.reverse()

    # --- Fetch post content ---
    posts_data = []
    fetched_urls = set()
    if os.path.exists(CONTENT_JSON_FILE):
        with open(CONTENT_JSON_FILE, "r", encoding="utf-8") as f:
            posts_data = json.load(f)
            fetched_urls = {post["url"] for post in posts_data}

    print("📄 Fetching individual posts...")
    for post in tqdm(all_posts, desc="Posts", unit="post"):
        if post["url"] in fetched_urls:
            continue
        content = fetch_post_content(post["url"])
        if content:
            posts_data.append(content)
            fetched_urls.add(post["url"])
            with open(CONTENT_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(posts_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Total posts fetched: {len(posts_data)}")

    # --- Create EPUB ---
    print("📚 Creating EPUB...")
    book = epub.EpubBook()
    book.set_identifier("ls001")
    book.set_title(CATEGORY_NAME.replace("_", " "))
    book.set_language("en")
    book.add_author("Reigokai Translations")

    chapters = []
    for idx, post in enumerate(tqdm(posts_data, desc="EPUB Chapters")):
        paragraphs = "".join(f"<p>{p}</p>" for p in post["content"].split("\n\n"))
        chapter = epub.EpubHtml(title=post["title"], file_name=f"chap_{idx+1}.xhtml", lang="en")
        chapter.content = f"<h1>{post['title']}</h1><h4>{post['date']}</h4>{paragraphs}"
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.spine = ["nav"] + chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub_file = os.path.join(OUTPUT_DIR, f"{CATEGORY_NAME}.epub")
    epub.write_epub(epub_file, book)
    print(f"✅ EPUB created: {epub_file}")

    # --- Create PDF ---
    FONT_PATH = ensure_font()
    print("📰 Creating PDF...")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, CATEGORY_NAME.replace("_", " "), ln=True, align="C")
    pdf.ln(10)

    for post in tqdm(posts_data, desc="PDF Posts"):
        pdf.set_font("DejaVu", "B", 14)
        pdf.multi_cell(0, 10, f"{post['title']} ({post['date']})")
        pdf.ln(2)
        pdf.set_font("DejaVu", "", 12)
        for para in post["content"].split("\n\n"):
            pdf.multi_cell(0, 8, para)
            pdf.ln(4)
        pdf.ln(10)

    pdf_file = os.path.join(OUTPUT_DIR, f"{CATEGORY_NAME}.pdf")
    pdf.output(pdf_file)
    print(f"✅ PDF created: {pdf_file}")
    print("🎉 All done!")


if __name__ == "__main__":
    run()
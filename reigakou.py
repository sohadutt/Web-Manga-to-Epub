import requests
import json
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from ebooklib import epub
from fpdf import FPDF

# --- CONFIG ---
CATEGORY_ID = 33
CATEGORY_NAME = "Living_Safely"
PER_PAGE = 100
CF_CLEARANCE = "GJgMiPJr9AMwH9teNh2f_eoaNppEm0IQAGurljcFe_g-1761404325-1.2.1.1-v_yCWypBE.NqBA6_G59hlTQacLTIKHavOZ76C9MYjpST9l4TzcTeJk_ne_abv_SdyUC7TpN_lt3Cuh2fTt0DGYau7xGrtvXHLaz_CNeeY1Evo1RH5QXrPpoXraoMSDOU4e_8kNZp.rSQZfn67PRAeo_VcYnPe1SaqXMNXTKwcugugoPlOKEUxxXhykFB7uSvgcgoEyS2P1uvGj3RBxwsVDnJhdipa0HT0uKfZOWJlfVcPv807ibtFgpZqSRZT5Ye"

BASE_URL = "https://reigokaitranslations.com/wp-json/wp/v2/posts"
API_JSON_FILE = f"{CATEGORY_NAME}_api.json"
POSTS_JSON_FILE = f"{CATEGORY_NAME}_posts.json"
OUTPUT_DIR = f"{CATEGORY_NAME}_ebook"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
    "Referer": f"https://reigokaitranslations.com/category/{CATEGORY_NAME.lower()}/",
    "Cookie": f"cf_clearance={CF_CLEARANCE}"
}

# --- HELPER FUNCTIONS ---
def clean_html(raw_html):
    """Strip HTML and return clean text."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def fetch_post_content(url):
    """Fetch the title, content, and date of a post from its URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("h1", class_="entry-title")
        content_tag = soup.find("div", class_="entry-content")
        date_tag = soup.find("time", class_="entry-date")

        return {
            "title": title_tag.get_text(strip=True) if title_tag else "No Title",
            "content": content_tag.get_text(separator="\n", strip=True) if content_tag else "No Content",
            "date": date_tag["datetime"] if date_tag and date_tag.has_attr("datetime") else "No Date",
            "url": url
        }

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

# --- FETCH API POSTS ---
if os.path.exists(API_JSON_FILE):
    with open(API_JSON_FILE, "r", encoding="utf-8") as f:
        all_posts = json.load(f)
else:
    all_posts = []
    page = 1
    with tqdm(desc="Fetching API pages", unit="page") as pbar:
        while True:
            url = f"{BASE_URL}?categories={CATEGORY_ID}&per_page={PER_PAGE}&page={page}"
            response = requests.get(url, headers=HEADERS)

            if response.status_code == 403:
                print("🚫 403 Forbidden — cf_clearance may be expired or invalid.")
                break
            elif response.status_code != 200:
                print(f"⚠️ Unexpected status code: {response.status_code}")
                break

            data = response.json()
            if not data:
                break

            for post in data:
                all_posts.append({
                    "title": post["title"]["rendered"],
                    "url": post["link"],
                    "date": post["date"]
                })

            page += 1
            pbar.update(1)

    with open(API_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

# --- LOAD EXISTING POST CONTENT ---
if os.path.exists(POSTS_JSON_FILE):
    with open(POSTS_JSON_FILE, "r", encoding="utf-8") as f:
        posts_data = json.load(f)
    fetched_urls = {post["url"] for post in posts_data}
else:
    posts_data = []
    fetched_urls = set()

# --- FETCH POST CONTENT ---
for post in tqdm(all_posts, desc="Fetching posts", unit="post"):
    if post["url"] in fetched_urls:
        continue
    post_content = fetch_post_content(post["url"])
    if post_content:
        posts_data.append(post_content)
        fetched_urls.add(post["url"])
        with open(POSTS_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Total posts saved: {len(posts_data)}")

# --- CREATE KINDLE-FRIENDLY EPUB ---
book = epub.EpubBook()
book.set_identifier("ls001")
book.set_title(CATEGORY_NAME.replace("_"," "))
book.set_language("en")
book.add_author("Reigokai Translations")

chapters = []
for idx, post in enumerate(tqdm(posts_data, desc="Creating EPUB chapters")):
    content_text = clean_html(post["content"])
    chapter = epub.EpubHtml(title=post["title"], file_name=f"chap_{idx+1}.xhtml", lang="en")
    chapter.content = f"<h1>{post['title']}</h1><h4>{post['date']}</h4><p>{content_text.replace('\n','<br/>')}</p>"
    book.add_item(chapter)
    chapters.append(chapter)

book.toc = tuple(chapters)
book.spine = ["nav"] + chapters
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

epub_file = os.path.join(OUTPUT_DIR, f"{CATEGORY_NAME}.epub")
epub.write_epub(epub_file, book)
print(f"✅ EPUB created: {epub_file}")

# --- CREATE PDF ---
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, CATEGORY_NAME.replace("_"," "), ln=True, align="C")
pdf.ln(10)

for post in tqdm(posts_data, desc="Adding posts to PDF"):
    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(0, 10, f"{post['title']} ({post['date']})")
    pdf.ln(2)

    pdf.set_font("Arial", "", 12)
    content_text = clean_html(post["content"])
    pdf.multi_cell(0, 8, content_text)
    pdf.ln(10)

pdf_file = os.path.join(OUTPUT_DIR, f"{CATEGORY_NAME}.pdf")
pdf.output(pdf_file)
print(f"✅ PDF created: {pdf_file}")
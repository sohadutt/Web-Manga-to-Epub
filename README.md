# WordPress Scraper & Ebook Generator 📚

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Project Status: Maintained](https://img.shields.io/badge/status-maintained-brightgreen.svg)](https://github.com/yourusername/living-safely-scraper)

A powerful Python script to scrape all posts from a specific WordPress category, bypass Cloudflare protection, and compile everything into a clean, offline-readable **EPUB** and **PDF**.

Perfect for archiving your favorite web novel, blog series, or serialized story (like "Living SAFELY") for offline reading on your Kindle, tablet, or phone.

## ✨ Features

* **WordPress API Scraper:** Fetches all posts from a specific category ID
* **Cloudflare Bypass:** Uses a `CF_CLEARANCE` cookie to access protected sites
* **Incremental Fetching:** Saves posts to a local JSON file
* **Multi-Format Ebook Generation:**
    * `EPUB`: A clean, Kindle-friendly file with a navigable table of contents
    * `PDF`: A universally readable document for any device
* **Smart & Configurable:** Easily set the target category ID, output names, and posts-per-page
* **Clean Output:** Uses `BeautifulSoup` to parse and clean HTML

## 🛠️ Prerequisites

Before you begin, you will need:

1. **Python 3.8+**
2. **Git** (to clone this repository)
3. A **valid `CF_CLEARANCE` cookie** from the target website

### Getting the CF_CLEARANCE Cookie

1. Open your web browser
2. Go to the target website
3. Open Developer Tools (`F12` or `Ctrl+Shift+I`)
4. Click on the **"Network"** tab
5. Refresh the page
6. Click on the first request
7. Go to **"Headers"** tab under **"Request Headers"**
8. Find and copy the `cf_clearance` cookie value

![How to find the CF_CLEARANCE cookie](https://i.imgur.com/gC5hJ6B.png)

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/living-safely-scraper.git
cd living-safely-scraper
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure
Create `.env` file:
```
CF_CLEARANCE=your_cookie_value_here
```

### 4. Run
```bash
python scraper.py
```

## 📂 Output Structure
```
reigakou-scraper-scraper/
├── Your_book_ebook/
│   ├── Your_book.epub
│   └── Your_book.pdf
├── Your_book_api.json
├── Your_book_posts.json
├── scraper.py
├── requirements.txt
├── .env
└── README.md
```

⚠️ **Disclaimer:** Use responsibly. For personal archiving only. Cookie expires periodically.

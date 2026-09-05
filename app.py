import os
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Setup Chrome Options (Headless Mode)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

BASE_URL = "https://movieboxhd.net/"

# Target Categories & A-Z Search Keywords
CATEGORY_URLS = [
    "https://movieboxhd.net/",
    "https://movieboxhd.net/web/movie",
    "https://movieboxhd.net/web/tv-series"
]

AZ_KEYWORDS = [chr(i) for i in range(97, 123)] + [str(n) for n in range(0, 10)]

def collect_all_moviebox_links():
    print("=== STARTING A-Z & CATEGORY SCRAPING FOR MOVIEBOXHD.NET ===")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    all_links = set()

    # 1. Scraping Category Base Pages with Auto-Scroll
    for cat_url in CATEGORY_URLS:
        print(f"\nCrawling Main Category: {cat_url}")
        try:
            driver.get(cat_url)
            time.sleep(3)
            
            # Scroll multiple times to trigger lazy-loaded movies
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href'].strip()
                full_url = urljoin(BASE_URL, href)
                if "/detail/" in full_url or "/movie/" in full_url or "/tv/" in full_url:
                    all_links.add(full_url)
                    
            print(f"Total collected so far: {len(all_links)}")
        except Exception as e:
            print(f"Error crawling {cat_url}: {e}")

    # 2. A-Z Keyword Search Crawling
    print("\n=== STARTING A-Z SEARCH KEYWORD CRAWLING ===")
    for kw in AZ_KEYWORDS:
        search_url = f"https://movieboxhd.net/web/search?keyword={kw}"
        print(f"Searching Keyword [{kw}]: {search_url}")
        try:
            driver.get(search_url)
            time.sleep(2.5)
            
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href'].strip()
                full_url = urljoin(BASE_URL, href)
                if "/detail/" in full_url or "/movie/" in full_url or "/tv/" in full_url:
                    all_links.add(full_url)
                    
            print(f"Total links after keyword [{kw}]: {len(all_links)}")
        except Exception as e:
            print(f"Error searching keyword [{kw}]: {e}")

    driver.quit()
    print(f"\n==========================================")
    print(f"TOTAL A-Z MOVIE/SERIES LINKS FOUND: {len(all_links)}")
    print(f"==========================================\n")
    return list(all_links)

def scrape_single_media_page(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Title Extraction
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Untitled Media"
        
        # Poster Extraction
        img_tag = soup.find('img')
        poster = ""
        if img_tag:
            poster = img_tag.get('src') or img_tag.get('data-src') or ""
        if not poster or not poster.startswith("http"):
            poster = "https://via.placeholder.com/300x450?text=No+Poster"
            
        # Player Iframe Extraction
        iframe = soup.find('iframe')
        player_src = iframe.get('src') if iframe else ""
        
        safe_name = "".join([c if c.isalnum() else "_" for c in title]).lower() + ".html"
        
        return {
            "title": title,
            "poster": poster,
            "player": player_src,
            "filename": safe_name
        }
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def build_movie_page(movie):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{movie['title']} - Watch Free on Flim360</title>
    <style>
        body {{ background-color: #0d0d0d; color: #ffffff; font-family: sans-serif; margin: 0; padding: 0; }}
        header {{ background: #161616; padding: 15px 30px; border-bottom: 2px solid #e50914; }}
        .logo {{ font-size: 26px; font-weight: bold; color: #e50914; text-decoration: none; }}
        .container {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; text-align: center; }}
        .poster {{ width: 220px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333; }}
        .player-box {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 10px; background: #000; border: 1px solid #e50914; }}
        .player-box iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}
        .btn-home {{ display: inline-block; margin-top: 25px; padding: 10px 20px; background: #e50914; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <header><a href="index.html" class="logo">FLIM360</a></header>
    <div class="container">
        <h1>{movie['title']}</h1>
        <img src="{movie['poster']}" class="poster" alt="{movie['title']}">
        <h3>Watch Online Free</h3>
        <div class="player-box">
            <iframe src="{movie['player']}" allowfullscreen></iframe>
        </div>
        <br><a href="index.html" class="btn-home">← Back to Flim360</a>
    </div>
</body>
</html>"""
    with open(movie['filename'], "w", encoding="utf-8") as f:
        f.write(html)

def build_homepage(movies):
    cards_html = ""
    for m in movies:
        cards_html += f"""
        <a href="{m['filename']}" class="card">
            <img src="{m['poster']}" alt="{m['title']}">
            <div class="card-title">{m['title']}</div>
        </a>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flim360 - Watch Movies & TV Series Free Online</title>
    <style>
        body {{ background-color: #0d0d0d; color: #ffffff; font-family: sans-serif; margin: 0; padding: 0; }}
        header {{ background: #161616; padding: 15px 30px; border-bottom: 2px solid #e50914; position: sticky; top: 0; z-index: 100; }}
        .logo {{ font-size: 32px; font-weight: bold; color: #e50914; text-decoration: none; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; padding: 30px; max-width: 1300px; margin: auto; }}
        .card {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; text-decoration: none; color: #fff; border: 1px solid #222; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); border-color: #e50914; }}
        .card img {{ width: 100%; height: 260px; object-fit: cover; }}
        .card-title {{ padding: 10px; font-size: 13px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    </style>
</head>
<body>
    <header><a href="index.html" class="logo">FLIM360</a></header>
    <h1 style="text-align: center; margin-top: 25px; font-weight: 300;">Latest Movies & TV Series</h1>
    <div class="grid">{cards_html}</div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    links = collect_all_moviebox_links()
    
    if links:
        scraped_movies = []
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        print(f"Scraping player details for all {len(links)} collected URLs...")
        
        for idx, link in enumerate(links, start=1):
            print(f"[{idx}/{len(links)}] Scraping: {link}")
            data = scrape_single_media_page(driver, link)
            
            if data and data['player']:
                build_movie_page(data)
                scraped_movies.append(data)
                
            # Batch Push to GitHub every 50 movies to keep changes synced
            if idx % 50 == 0:
                build_homepage(scraped_movies)
                os.system("git add .")
                os.system(f'git commit -m "Auto batch push ({idx} movies/series)"')
                os.system("git push origin main")
                print(f"--- Batch {idx} synced to GitHub ---")
                
        driver.quit()
        
        if scraped_movies:
            build_homepage(scraped_movies)
            os.system("git add .")
            os.system('git commit -m "MovieBoxHD A-Z Full Crawl Complete"')
            os.system("git push origin main")
            print("\nSUCCESS! All A-Z Movies & Series published to Flim360.")
    else:
        print("No media links collected.")
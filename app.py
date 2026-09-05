import os
import time
import requests
from bs4 import BeautifulSoup

SITEMAP_URL = "https://movie-box.co/sitemap.xml" # Target site sitemap
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_movie_links():
    print("Fetching sitemap links...")
    try:
        response = requests.get(SITEMAP_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        urls = [url.text for url in soup.find_all('loc')]
        # Filter movie/post links (ignoring categories/pages)
        movie_urls = [u for u in urls if '/movie/' in u or '/series/' in u or u.count('/') > 3]
        return movie_urls[:20]  # First batch of 20 movies for testing
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

def scrape_movie_page(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title = soup.find('h1').text.strip() if soup.find('h1') else "Untitled Movie"
        
        # Poster image
        img_tag = soup.find('img', {'class': 'wp-post-image'}) or soup.find('img')
        poster = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "https://via.placeholder.com/300x450"
        
        # Embed Player URL
        iframe = soup.find('iframe')
        player_src = iframe['src'] if iframe and 'src' in iframe.attrs else ""
        
        # Safe filename for HTML
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
        body {{ background-color: #0f0f0f; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
        header {{ background: #1a1a1a; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e50914; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e50914; text-decoration: none; }}
        .container {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; text-align: center; }}
        .poster {{ width: 220px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3); }}
        .player-box {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 10px; background: #000; margin-top: 20px; border: 1px solid #333; }}
        .player-box iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}
        .btn-home {{ display: inline-block; margin-top: 25px; padding: 10px 20px; background: #e50914; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <header><a href="index.html" class="logo">FLIM360</a></header>
    <div class="container">
        <h1>{movie['title']}</h1>
        <img src="{movie['poster']}" class="poster" alt="{movie['title']}">
        <h3>Watch Online (100% Free)</h3>
        <div class="player-box">
            <iframe src="{movie['player']}" allowfullscreen></iframe>
        </div>
        <br><a href="index.html" class="btn-home">← Back to Flim360 Home</a>
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
    <title>Flim360 - Watch Movies & Series Free Online</title>
    <style>
        body {{ background-color: #0f0f0f; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
        header {{ background: #1a1a1a; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e50914; sticky: top; }}
        .logo {{ font-size: 28px; font-weight: bold; color: #e50914; text-decoration: none; letter-spacing: 1px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; padding: 30px; max-width: 1300px; margin: auto; }}
        .card {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; text-decoration: none; color: #fff; transition: transform 0.2s, box-shadow 0.2s; border: 1px solid #222; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4); border-color: #e50914; }}
        .card img {{ width: 100%; height: 260px; object-fit: cover; }}
        .card-title {{ padding: 10px; font-size: 14px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    </style>
</head>
<body>
    <header>
        <a href="index.html" class="logo">FLIM360</a>
    </header>
    <h2 style="text-align: center; margin-top: 20px; color: #ccc;">Latest Movies & Dramas</h2>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    links = get_movie_links()
    scraped_movies = []
    
    print(f"Found {len(links)} links. Scraping now...")
    for link in links:
        data = scrape_movie_page(link)
        if data and data['player']:
            build_movie_page(data)
            scraped_movies.append(data)
            print(f"Added: {data['title']}")
        time.sleep(1) # Delay to prevent blocking
        
    build_homepage(scraped_movies)
    print("Homepage updated successfully!")

    # Push to GitHub
    os.system("git add .")
    os.system('git commit -m "Updated Flim360 with sitemap movies"')
    os.system("git push origin main")
    print("Flim360 updated live on GitHub Pages!")
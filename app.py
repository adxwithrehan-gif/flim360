import os
import time
import requests
from bs4 import BeautifulSoup

# Target Movie Page Scrape Function
def scrape_movie_data(movie_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('h1').text.strip() if soup.find('h1') else "Movie Title"
    poster = soup.find('img', {'class': 'wp-post-image'})['src'] if soup.find('img', {'class': 'wp-post-image'}) else ""
    
    # Extract Streaming Embed Link
    iframe_tag = soup.find('iframe')
    stream_link = iframe_tag['src'] if iframe_tag else ""
    
    return {
        "title": title,
        "poster": poster,
        "stream_link": stream_link
    }

# Static HTML Generator
def create_html_page(data, filename):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{data['title']} - Watch Online</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #141414; color: #fff; text-align: center; padding: 20px; }}
        img {{ max-width: 300px; border-radius: 8px; margin-bottom: 20px; }}
        .player {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 800px; margin: auto; }}
        .player iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}
    </style>
</head>
<body>
    <h1>{data['title']}</h1>
    <img src="{data['poster']}" alt="{data['title']}">
    <h3>Watch Online:</h3>
    <div class="player">
        <iframe src="{data['stream_link']}" allowfullscreen></iframe>
    </div>
</body>
</html>"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    # Test link
    sample_url = "https://movie-box.co/"
    
    print("Scraping movie data...")
    movie_data = scrape_movie_data(sample_url)
    
    file_name = "index.html"
    create_html_page(movie_data, file_name)
    print(f"Created {file_name} successfully!")

    # Auto Commit & Push to GitHub
    os.system("git add .")
    os.system('git commit -m "Auto added new movie"')
    os.system("git push origin main")
    print("Uploaded to GitHub Pages successfully!")
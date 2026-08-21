import os
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests

TARGET_URL = "https://cu.edu.tr/sayfalar/tum-duyurular"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def generate_rss():
    response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    fg = FeedGenerator()
    fg.id(TARGET_URL)
    fg.title("Örnek Site Güncel Duyurular")
    fg.link(href=TARGET_URL, rel="alternate")
    fg.description("Otomatik üretilen özel RSS akışı")
    fg.language("tr")

    # Sayfadaki haber/duyuru kutularını seçin
    items = soup.select(".duyuru-listesi .duyuru-item")

    for item in items[:15]:  # Son 15 içeriği al
        title_elem = item.select_one("a.baslik")
        if not title_elem:
            continue

        title = title_elem.get_text(strip=True)
        link = title_elem.get("href", "")
        if not link.startswith("http"):
            link = requests.compat.urljoin(TARGET_URL, link)

        desc_elem = item.select_one(".ozet")
        description = desc_elem.get_text(strip=True) if desc_elem else title

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.description(description)

    # Dosyayı ana dizine yaz
    fg.rss_file("feed.xml", pretty=True)

if __name__ == "__main__":
    generate_rss()

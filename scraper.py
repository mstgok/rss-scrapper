import html
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Hedef duyuru sayfasının URL'si
TARGET_URL = "https://www.cu.edu.tr/sayfalar/tum-duyurular"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def generate_rss():
  response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
  response.raise_for_status()

  # Karakter kodlama uyumsuzluğunu önlemek için utf-8 ayarı
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  fg = FeedGenerator()
  fg.id(TARGET_URL)
  fg.title("Çukurova Üniversitesi Duyuruları")
  fg.link(href=TARGET_URL, rel="alternate")
  fg.description("Güncel üniversite ve bölüm duyuruları akışı")
  fg.language("tr")

  # Her bir duyuru bloğunu yakala
  entries = soup.select("div.entry")

  for entry in entries:
    # 1. Başlık ve URL alma
    link_elem = entry.select_one(".entry-title h2 a")
    if not link_elem:
      continue

    raw_title = link_elem.get_text(strip=True)
    title = html.unescape(raw_title)  # HTML entity karakterlerini düzelt

    link = link_elem.get("href", "").strip()
    if not link.startswith("http"):
      link = requests.compat.urljoin(TARGET_URL, link)

    # 2. Tarih bilgisini meta alanından çekme
    date_elem = entry.select_one(".entry-meta li:has(i.icon-calender3)")
    date_text = date_elem.get_text(strip=True) if date_elem else ""

    description = f"Yayın Tarihi: {date_text}" if date_text else title

    # 3. RSS girdisi oluşturma
    fe = fg.add_entry()
    fe.id(link)
    fe.title(title)
    fe.link(href=link)
    fe.description(description)

  # Dosyayı ana dizine yaz
  fg.rss_file("feed.xml", pretty=True)


if __name__ == "__main__":
  generate_rss()

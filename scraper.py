
import html
import xml.dom.minidom
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests

# Hedef duyuru sayfasının URL'si
TARGET_URL = "https://www.cu.edu.tr/sayfalar/tum-duyurular"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def generate_rss():
  response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
  response.raise_for_status()
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  fg = FeedGenerator()
  fg.id(TARGET_URL)
  fg.title("Çukurova Üniversitesi Duyuruları")
  fg.link(href=TARGET_URL, rel="alternate")
  fg.description("Güncel duyurular akışı")
  fg.language("tr")

  entries = soup.select("div.entry")

  for entry in entries:
    link_elem = entry.select_one(".entry-title h2 a")
    if not link_elem:
      continue

    title = html.unescape(link_elem.get_text(strip=True))
    link = link_elem.get("href", "").strip()
    if not link.startswith("http"):
      link = requests.compat.urljoin(TARGET_URL, link)

    date_elem = entry.select_one(".entry-meta li:has(i.icon-calender3)")
    date_text = date_elem.get_text(strip=True) if date_elem else ""
    description = f"Yayın Tarihi: {date_text}" if date_text else title

    fe = fg.add_entry()
    fe.id(link)
    fe.title(title)
    fe.link(href=link)
    fe.description(description)

  # --- Düzgün Girintili (Pretty-Print) XML Kaydı ---
  raw_rss = fg.rss_str()
  dom = xml.dom.minidom.parseString(raw_rss)
  pretty_xml = dom.toprettyxml(indent="  ", encoding="utf-8")

  with open("feed.xml", "wb") as f:
    f.write(pretty_xml)


if __name__ == "__main__":
  generate_rss()

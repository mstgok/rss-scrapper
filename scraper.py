import html
import xml.dom.minidom
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests

import re
import urllib3
import requests

# SSL uyarılarını susturmak için (gerekirse)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}
def save_pretty_xml(fg, filename):
  """Feed nesnesini düzgün girintili XML dosyası olarak kaydeder."""
  raw_rss = fg.rss_str()
  dom = xml.dom.minidom.parseString(raw_rss)
  pretty_xml = dom.toprettyxml(indent="  ", encoding="utf-8")
  with open(filename, "wb") as f:
    f.write(pretty_xml)


# -------------------------------------------------------------
# 1. SİTE: Çukurova Üniversitesi Genel Duyurular
# -------------------------------------------------------------
def scrape_universite():
  url = "https://www.cu.edu.tr/sayfalar/tum-duyurular"
  fg = FeedGenerator()
  fg.id(url)
  fg.title("Çukurova Üniversitesi Duyuruları")
  fg.link(href=url, rel="alternate")
  fg.description("Genel Üniversite Duyuruları")
  fg.language("tr")

  try:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    for entry in soup.select("div.entry")[:15]:
      link_elem = entry.select_one(".entry-title h2 a")
      if not link_elem:
        continue

      title = html.unescape(link_elem.get_text(strip=True))
      link = link_elem.get("href", "").strip()
      if not link.startswith("http"):
        link = requests.compat.urljoin(url, link)

      date_elem = entry.select_one(".entry-meta li:has(i.icon-calender3)")
      date_text = date_elem.get_text(strip=True) if date_elem else ""

      desc = f"""
            <p><strong>Yayın Tarihi:</strong> {date_text}</p>
            <p><a href="{link}" target="_blank">🔗 Duyuru Detayı İçin Tıklayınız &raquo;</a></p>
            """

      fe = fg.add_entry()
      fe.id(link)
      fe.title(title)
      fe.link(href=link, rel="alternate")
      fe.description(desc)

    save_pretty_xml(fg, "feed_universite.xml")
    print("✓ Üniversite duyuruları başarıyla güncellendi.")
  except Exception as e:
    print(f"✗ Üniversite kazıma hatası: {e}")


# -------------------------------------------------------------
# 2. SİTE: Hacettepe Üniversitesi Öğrenci Duyuruları
# -------------------------------------------------------------
def scrape_hacettepe():
  url = "https://oidb.hacettepe.edu.tr/tr/duyurular"
  fg = FeedGenerator()
  fg.id(url)
  fg.title("Hacettepe Üniversitesi ÖİDB Duyuruları")
  fg.link(href=url, rel="alternate")
  fg.description(
      "Hacettepe Üniversitesi Öğrenci İşleri Daire Başkanlığı Duyuruları"
  )
  fg.language("tr")

  try:
    # verify=False ekleyerek SSL el sıkışma hatalarını aşıyoruz
    resp = requests.get(url, headers=HEADERS, timeout=20, verify=False)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # Hacettepe ÖİDB sayfasındaki olası tüm duyuru kapsayıcılarını tara
    items = soup.select("table tbody tr, .list-group-item, .duyuru, .announcement-item")

    # Eğer özel kapsayıcı bulunamazsa doğrudan duyuru linki içeren a etiketlerini topla
    if not items:
      items = soup.find_all("a", href=re.compile(r"/duyurular/|/haber/|/duyuru/"))

    valid_entries = 0

    for item in items[:25]:
      link_elem = item if item.name == "a" else item.select_one("a")
      if not link_elem:
        continue

      title = html.unescape(link_elem.get_text(strip=True))
      # Boş veya çok kısa menü linklerini atla
      if len(title) < 5 or title.lower() in ["tümü", "detay", "devamı"]:
        continue

      link = link_elem.get("href", "").strip()
      if not link.startswith("http"):
        link = requests.compat.urljoin(url, link)

      # Tarih tespiti
      item_text = item.get_text(" ", strip=True)
      date_match = re.search(r"\d{2}[./-]\d{2}[./-]\d{4}", item_text) or re.search(
          r"\d{4}[./-]\d{2}[./-]\d{2}", item_text
      )
      date_text = date_match.group(0) if date_match else "Güncel"

      html_description = f"""
            <p><strong>Yayın Tarihi:</strong> {date_text}</p>
            <p><a href="{link}" target="_blank" rel="noopener noreferrer">🔗 Hacettepe ÖİDB Duyuru Detayı &raquo;</a></p>
            """

      fe = fg.add_entry()
      fe.id(link)
      fe.title(title)
      fe.link(href=link, rel="alternate")
      fe.description(html_description)
      valid_entries += 1

    if valid_entries > 0:
      save_pretty_xml(fg, "feed_hacettepe.xml")
      print(f"✓ [feed_hacettepe.xml] {valid_entries} duyuru ile başarıyla oluşturuldu.")
    else:
      print("⚠ Hacettepe sayfasından duyuru ayrıştırılamadı (0 girdi).")

  except Exception as e:
    print(f"✗ Hacettepe kazıma hatası: {type(e).__name__} - {e}")


if __name__ == "__main__":
  scrape_universite()
  scrape_hacettepe()

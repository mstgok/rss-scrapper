import html
import xml.dom.minidom
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
  fg.description("Hacettepe Üniversitesi Öğrenci İşleri Daire Başkanlığı Duyuruları")
  fg.language("tr")

  try:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    # Hacettepe ÖİDB duyuruları DataTables tablosundaki <tr> satırlarıdır
    rows = soup.select("table tbody tr")

    for row in rows[:20]:
      link_elem = row.select_one("a")
      if not link_elem:
        continue

      title = html.unescape(link_elem.get_text(strip=True))
      link = link_elem.get("href", "").strip()
      if not link.startswith("http"):
        link = requests.compat.urljoin(url, link)

      # Tablodaki tarih sütununu veya metin içerisindeki YYYY-MM-DD tarih formatını yakala
      row_text = row.get_text(" ", strip=True)
      date_match = re.search(r"\d{4}-\d{2}-\d{2}", row_text) or re.search(
          r"\d{2}\.\d{2}\.\d{4}", row_text
      )
      date_text = date_match.group(0) if date_match else "Belirtilmedi"

      html_description = f"""
            <p><strong>Yayın Tarihi:</strong> {date_text}</p>
            <p><a href="{link}" target="_blank" rel="noopener noreferrer">🔗 Hacettepe ÖİDB Duyuru Detayı &raquo;</a></p>
            """

      fe = fg.add_entry()
      fe.id(link)
      fe.title(title)
      fe.link(href=link, rel="alternate")
      fe.description(html_description)

    save_pretty_xml(fg, "feed_hacettepe.xml")
    print("✓ [feed_hacettepe.xml] başarıyla oluşturuldu.")
  except Exception as e:
    print(f"✗ Hacettepe kazıma hatası: {e}")


if __name__ == "__main__":
  scrape_universite()
  scrape_hacettepe()

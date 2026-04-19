import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime


class Crawler:
    """
    A polite web crawler for quotes.toscrape.com.
    Crawls quote pages, extracts clean text, and discovers pagination links.
    """

    def __init__(self, base_url, delay=6):
        self.base_url = base_url
        self.delay = delay
        self.visited = set()
        self.to_visit = [base_url]

    def timestamp(self):
        """Return current timestamp as a readable string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fetch_page(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[{self.timestamp()}] [ERROR] Failed to fetch {url}: {e}")
            return None

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup, current_url):
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(current_url, href)

            if (
                full_url.startswith(self.base_url)
                and "/page/" in full_url
                and "/tag/" not in full_url
                and "/author/" not in full_url
            ):
                links.add(full_url)

        return links

    def crawl(self):
        pages = {}

        while self.to_visit:
            url = self.to_visit.pop(0)

            if url in self.visited:
                continue

            print(f"[{self.timestamp()}] [CRAWLING] {url}")

            html = self.fetch_page(url)
            if html is None:
                continue

            soup, text = self.parse_page(html)
            pages[url] = text
            self.visited.add(url)

            for link in self.extract_links(soup, url):
                if link not in self.visited and link not in self.to_visit:
                    self.to_visit.append(link)

            time.sleep(self.delay)

        return pages

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Crawler:
    """
    A polite web crawler for quotes.toscrape.com.
    Crawls pages, extracts clean text, and discovers internal links.
    """

    def __init__(self, base_url, delay=6):
        self.base_url = base_url
        self.delay = delay
        self.visited = set()
        self.to_visit = [base_url]

    def fetch_page(self, url, retries=2):
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"[ERROR] Failed to fetch {url} (attempt {attempt + 1}): {e}")
                time.sleep(self.delay)
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
            full_url = urljoin(current_url, a["href"])
            if full_url.startswith(self.base_url):
                links.add(full_url)

        return links

    def crawl(self):
        pages = {}

        while self.to_visit:
            url = self.to_visit.pop(0)

            if url in self.visited:
                continue

            print(f"[CRAWLING] {url}")
            html = self.fetch_page(url)

            if html is None:
                continue

            soup, text = self.parse_page(html)
            pages[url] = text
            self.visited.add(url)

            for link in self.extract_links(soup, url):
                if link not in self.visited and link not in self.to_visit:
                    self.to_visit.append(link)

            time.sleep(self.delay)  # politeness window

        return pages
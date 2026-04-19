import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
from typing import Dict, Set, Tuple


class Crawler:
    """
    Polite web crawler for quotes.toscrape.com.

    - Respects politeness window
    - Extracts clean visible text
    - Crawls internal links only
    """

    def __init__(self, base_url: str, delay: int = 6):
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.visited: Set[str] = set()
        self.to_visit: deque[str] = deque([self.base_url])
        self.base_domain = urlparse(self.base_url).netloc

    def fetch_page(self, url: str, retries: int = 2) -> str | None:
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"[ERROR] {url} (attempt {attempt}): {e}")
                time.sleep(self.delay)
        return None

    def parse_page(self, html: str) -> Tuple[BeautifulSoup, str]:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            resolved = urljoin(current_url, href)
            resolved, _ = urldefrag(resolved)

            if urlparse(resolved).netloc == self.base_domain:
                links.add(resolved.rstrip("/"))

        return links

    def crawl(self) -> Dict[str, str]:
        pages: Dict[str, str] = {}

        while self.to_visit:
            url = self.to_visit.popleft()

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
                if link not in self.visited:
                    self.to_visit.append(link)

            time.sleep(self.delay)

        return pages
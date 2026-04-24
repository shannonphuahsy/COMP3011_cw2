import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
from typing import Dict, Set, Tuple


class Crawler:
    """
    Polite web crawler for https://quotes.toscrape.com

    Features:
    - Respects politeness delay (>= 6 seconds)
    - Crawls pagination pages (/page/N)
    - Extracts visible text
    - Handles network errors with retries
    """

    def __init__(self, base_url: str, delay: int = 6):
        self.base_url = base_url.rstrip("/")
        self.delay = delay

        self.visited: Set[str] = set()
        self.to_visit: deque[str] = deque([self.base_url])

        self.base_domain = urlparse(self.base_url).netloc

    def fetch_page(self, url: str, retries: int = 3) -> str | None:
        """Download page HTML with retry logic."""
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] [ERROR] {url} (attempt {attempt}): {e}")
                time.sleep(self.delay)
        return None

    def parse_page(self, html: str) -> Tuple[BeautifulSoup, str]:
        """Parse HTML and extract visible text."""
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup: BeautifulSoup) -> Set[str]:

        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            resolved = urljoin(self.base_url, href)
            resolved, _ = urldefrag(resolved)

            parsed = urlparse(resolved)

            if parsed.netloc != self.base_domain:
                continue

            path = parsed.path.rstrip("/")

            # Homepage
            if path == "":
                links.add(self.base_url)
                continue

            # Pagination pages only
            if path.startswith("/page/") and path[6:].isdigit():
                links.add(f"{self.base_url}{path}")

        return links

    def crawl(self) -> Dict[str, str]:
        """
        Crawl pagination pages using BFS.

        Returns:
            dict[url] -> page text
        """
        pages: Dict[str, str] = {}

        while self.to_visit:
            url = self.to_visit.popleft()

            if url in self.visited:
                continue

            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] [CRAWLING] {url}")

            html = self.fetch_page(url)
            if html is None:
                continue

            soup, text = self.parse_page(html)
            pages[url] = text
            self.visited.add(url)

            for link in self.extract_links(soup):
                if link not in self.visited and link not in self.to_visit:
                    self.to_visit.append(link)

            time.sleep(self.delay)

        print(f"\n[Crawl complete] {len(pages)} pages indexed.")
        return pages
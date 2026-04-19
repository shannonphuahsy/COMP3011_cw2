import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


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
        """
        Fetch a page with basic retry logic.
        """
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
        """
        Parse HTML and extract visible text.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove non-visible elements
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup, current_url):
        """
        Extract internal links (same domain only).
        """
        links = set()
        base_domain = urlparse(self.base_url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(current_url, href)

            # Keep only links within the same domain
            if urlparse(full_url).netloc == base_domain:
                links.add(full_url)

        return links

    def crawl(self):
        """
        Crawl all reachable pages starting from the base URL.
        Returns a dictionary: {url: page_text}
        """
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

            # Politeness window
            time.sleep(self.delay)

        return pages
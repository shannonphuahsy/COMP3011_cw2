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
        """
        :param base_url: Starting URL for the crawler
        :param delay: Politeness delay between requests (seconds)
        """
        self.base_url = base_url
        self.delay = delay
        self.visited = set()
        self.to_visit = [base_url]

    def fetch_page(self, url):
        """
        Fetch a page safely using HTTP GET.
        Returns page HTML or None on failure.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None

    def parse_page(self, html):
        """
        Parse HTML and extract visible text.
        Returns (BeautifulSoup object, cleaned text).
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup, current_url):
        """
        Extract valid internal links from a page.
        """
        links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(current_url, href)

            # Only crawl pages within the target website
            if full_url.startswith(self.base_url):
                links.add(full_url)

        return links

    def crawl(self):
        """
        Crawl all pages starting from the base URL.
        Returns a dictionary: {url: page_text}
        """
        pages = {}

        while self.to_visit:
            current_url = self.to_visit.pop(0)

            if current_url in self.visited:
                continue

            print(f"[CRAWLING] {current_url}")

            html = self.fetch_page(current_url)
            if html is None:
                continue

            soup, text = self.parse_page(html)
            pages[current_url] = text
            self.visited.add(current_url)

            new_links = self.extract_links(soup, current_url)
            for link in new_links:
                if link not in self.visited and link not in self.to_visit:
                    self.to_visit.append(link)

            # Politeness window
            time.sleep(self.delay)

        return pages
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
from typing import Dict, Set, Tuple


class Crawler:
    """
    A polite web crawler for https://quotes.toscrape.com.

    Responsibilities:
    - Crawl the target website starting from the base URL
    - Discover pagination pages 
    - Respect a politeness window of at least 6 seconds between requests
    - Handle network errors gracefully with retry logic
    - Extract clean, visible text from each page for indexing

    Design decisions:
    - Breadth-first search (BFS) is used for predictable traversal
    - Crawling is restricted to pagination pages to avoid tag-based duplication
    - All URLs are normalised to avoid duplicates
    """

    def __init__(self, base_url: str, delay: int = 6):
        """
        Initialise the crawler.

        Args:
            base_url (str): The starting URL for the crawl.
            delay (int): Politeness delay (seconds) between HTTP requests.
        """
        # Normalise base URL to avoid trailing slash mismatches
        self.base_url = base_url.rstrip("/")
        self.delay = delay

        # Track visited URLs to avoid re-crawling the same page
        self.visited: Set[str] = set()

        # Queue for BFS traversal, starting from the base URL
        self.to_visit: deque[str] = deque([self.base_url])

        # Domain restriction to ensure only internal pages are crawled
        self.base_domain = urlparse(self.base_url).netloc

    def fetch_page(self, url: str, retries: int = 3) -> str | None:
        """
        Fetch the HTML content of a page from the given URL.

        Network errors are handled gracefully by retrying the request.
        If all retries fail, the function returns None.

        Args:
            url (str): URL of the page to fetch.
            retries (int): Number of retry attempts on failure.

        Returns:
            str | None: HTML content of the page, or None if fetching fails.
        """
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                return response.text

            except requests.RequestException as e:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] [ERROR] {url} (attempt {attempt}): {e}")

                # Respect politeness window even after an error
                time.sleep(self.delay)

        return None

    def parse_page(self, html: str) -> Tuple[BeautifulSoup, str]:
        """
        Parse HTML content and extract visible text.

        Non-visible elements such as scripts and styles are removed
        so the index only contains meaningful page content.

        Args:
            html (str): Raw HTML of a page.

        Returns:
            Tuple[BeautifulSoup, str]:
                - Parsed BeautifulSoup object
                - Clean visible text extracted from the page
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove elements that do not contribute to visible content
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return soup, text

    def extract_links(self, soup: BeautifulSoup) -> Set[str]:
        """
        Extract valid internal pagination links from a page.

        Allowed URLs:
        - Homepage (base URL)
        - Pagination pages of the form /page/<number>

        Ignored URLs:
        - Tag pages (/tag/...)
        - Author pages
        - External websites

        Args:
            soup (BeautifulSoup): Parsed HTML of the current page.

        Returns:
            Set[str]: A set of normalised pagination URLs to crawl next.
        """
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            # Resolve relative links and remove URL fragments
            resolved = urljoin(self.base_url, href)
            resolved, _ = urldefrag(resolved)

            parsed = urlparse(resolved)

            # Enforce same-domain restriction
            if parsed.netloc != self.base_domain:
                continue

            path = parsed.path.rstrip("/")

            # Homepage
            if path == "":
                links.add(self.base_url)
                continue

            # Pagination pages only (e.g. /page/1, /page/2)
            if path.startswith("/page/") and path[6:].isdigit():
                links.add(f"{self.base_url}{path}")

        return links

    def crawl(self) -> Dict[str, str]:
        """
        Crawl the website using breadth-first search (BFS).

        Each page is fetched, parsed, and stored exactly once.
        A politeness delay is enforced between all HTTP requests.

        Returns:
            Dict[str, str]: Mapping of URL -> visible page text.
        """
        pages: Dict[str, str] = {}

        while self.to_visit:
            url = self.to_visit.popleft()

            # Skip pages that have already been processed
            if url in self.visited:
                continue

            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] [CRAWLING] {url}")

            html = self.fetch_page(url)
            if html is None:
                # Skip failed pages but continue crawling
                continue

            soup, text = self.parse_page(html)

            pages[url] = text
            self.visited.add(url)

            # Discover new pagination links for BFS traversal
            for link in self.extract_links(soup):
                if link not in self.visited and link not in self.to_visit:
                    self.to_visit.append(link)

            # Mandatory politeness window
            time.sleep(self.delay)

        print(f"\n[Crawl complete] {len(pages)} pages indexed.")
        return pages
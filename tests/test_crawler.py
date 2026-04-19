import sys
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
import requests

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crawler import Crawler


# =========================
# Parsing-related tests
# =========================

def test_parse_page_removes_non_visible_elements():
    """
    The crawler should remove script and style elements
    and return only visible page text.
    """
    crawler = Crawler("https://example.com")

    html = """
    <html>
        <head>
            <style>.hidden {}</style>
            <script>alert("xss")</script>
        </head>
        <body>
            <p>Hello world</p>
        </body>
    </html>
    """

    _, text = crawler.parse_page(html)

    assert "alert" not in text
    assert "hidden" not in text
    assert "Hello world" in text


# =========================
# Link-extraction tests
# =========================

def test_extracts_only_internal_links():
    """
    The crawler should only keep links within
    the same domain as the base URL.
    """
    crawler = Crawler("https://example.com")

    soup = BeautifulSoup("""
        <a href="/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <a href="https://external.com/page">External</a>
    """, "html.parser")

    links = crawler.extract_links(soup, "https://example.com")

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://external.com/page" not in links


# =========================
# Network / fetching tests
# =========================

@patch("crawler.requests.get")
def test_fetch_page_success(mock_get):
    """
    fetch_page should return page HTML
    when the HTTP request succeeds.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html>OK</html>"
    mock_get.return_value.raise_for_status = lambda: None

    crawler = Crawler("https://example.com")
    html = crawler.fetch_page("https://example.com")

    assert html == "<html>OK</html>"


@patch("crawler.requests.get")
def test_fetch_page_failure_returns_none(mock_get):
    """
    fetch_page should fail gracefully and
    return None when a RequestException occurs.
    """
    mock_get.side_effect = requests.RequestException("Network failure")

    crawler = Crawler("https://example.com")
    html = crawler.fetch_page("https://example.com", retries=1)

    assert html is None
import sys
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crawler import Crawler


def test_parse_page_removes_scripts_and_styles():
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

    soup, text = crawler.parse_page(html)

    assert "alert" not in text
    assert "hidden" not in text
    assert "Hello world" in text


def test_extract_links_internal_links_only():
    crawler = Crawler("https://example.com")

    soup = BeautifulSoup("""
        /page1Page 1</a>
        https://example.com/page2Page 2</a>
        https://external.com/pageExternal</a>
    """, "html.parser")

    links = crawler.extract_links(soup, "https://example.com")

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://external.com/page" not in links


@patch("crawler.requests.get")
def test_fetch_page_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html>OK</html>"
    mock_get.return_value.raise_for_status = lambda: None

    crawler = Crawler("https://example.com")
    html = crawler.fetch_page("https://example.com")

    assert html == "<html>OK</html>"


@patch("crawler.requests.get")
def test_fetch_page_failure_returns_none(mock_get):
    mock_get.side_effect = Exception("Network error")

    crawler = Crawler("https://example.com")
    html = crawler.fetch_page("https://example.com", retries=1)

    assert html is None
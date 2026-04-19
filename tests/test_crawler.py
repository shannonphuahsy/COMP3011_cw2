from src.crawler import Crawler
from bs4 import BeautifulSoup


def test_parse_page_removes_scripts():
    crawler = Crawler("https://example.com")

    html = """
    <html>
        <head><script>alert("x")</script></head>
        <body><p>Hello world</p></body>
    </html>
    """

    soup, text = crawler.parse_page(html)

    assert "alert" not in text
    assert "Hello world" in text


def test_extract_links_internal_only():
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
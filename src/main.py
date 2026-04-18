from crawler import Crawler

if __name__ == "__main__":
    crawler = Crawler("https://quotes.toscrape.com/")
    pages = crawler.crawl()
    print(f"\nCrawled {len(pages)} pages successfully.")
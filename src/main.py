from crawler import Crawler
from indexer import InvertedIndex

if __name__ == "__main__":
    crawler = Crawler("https://quotes.toscrape.com/")
    pages = crawler.crawl()

    print(f"Crawled {len(pages)} pages successfully.")

    index = InvertedIndex()
    index.build_from_pages(pages)

    # Test: print index entry for a word
    word = "life"
    entry = index.get_word(word)

    print(f"\nInverted index for '{word}':")
    for url, data in entry.items():
        print(f"{url} -> count: {data['count']}")
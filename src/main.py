import sys
from crawler import Crawler
from indexer import InvertedIndex

INDEX_FILE = "data/index.json"
BASE_URL = "https://quotes.toscrape.com/"


def build():
    print("Building index (this will crawl the website)...")

    crawler = Crawler(BASE_URL)
    pages = crawler.crawl()

    index = InvertedIndex()
    index.build_from_pages(pages)
    index.save(INDEX_FILE)

    print("Index built and saved.")


def load_index():
    index = InvertedIndex()
    index.load(INDEX_FILE)
    print("Index loaded.")
    return index


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/main.py build")
        print("  python src/main.py load")
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "load":
        load_index()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
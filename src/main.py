import sys
from crawler import Crawler
from indexer import InvertedIndex
from search import SearchEngine

BASE_URL = "https://quotes.toscrape.com/"
INDEX_FILE = "data/index.json"


def build():
    print("Building index (this will crawl the website)...")
    crawler = Crawler(BASE_URL)
    pages = crawler.crawl()

    index = InvertedIndex()
    index.build_from_pages(pages)
    index.save(INDEX_FILE)

    print("Index built and saved.")


def load():
    index = InvertedIndex()
    index.load(INDEX_FILE)
    print("Index loaded successfully.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/main.py build")
        print("  python src/main.py load")
        print("  python src/main.py print <word>")
        print("  python src/main.py find <word1> <word2> ...")
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "load":
        load()

    elif command == "print":
        if len(sys.argv) != 3:
            print("Usage: python src/main.py print <word>")
            return
        search = SearchEngine()
        print(search.print_word(sys.argv[2]))

    elif command == "find":
        if len(sys.argv) < 3:
            print("Usage: python src/main.py find <word1> <word2> ...")
            return
        search = SearchEngine()
        print(search.find_query(sys.argv[2:]))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
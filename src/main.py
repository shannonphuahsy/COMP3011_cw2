import sys
from crawler import Crawler
from indexer import InvertedIndex
from search import SearchEngine

BASE_URL = "https://quotes.toscrape.com"
INDEX_FILE = "data/index.json"


def build():
    crawler = Crawler(BASE_URL)
    pages = crawler.crawl()

    index = InvertedIndex()
    index.build_from_pages(pages)
    index.save(INDEX_FILE)

    print("[DONE] Index built and saved.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  build")
        print("  print <word>")
        print("  find <word1> <word2> ...")
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "print":
        search = SearchEngine()
        print(search.print_word(sys.argv[2]))

    elif command == "find":
        search = SearchEngine()
        print(search.find_query(sys.argv[2:]))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
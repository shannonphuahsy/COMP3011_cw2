import sys
from crawler import Crawler
from indexer import InvertedIndex
from search import SearchEngine

BASE_URL = "https://quotes.toscrape.com"
INDEX_FILE = "data/index.json"


def build():
    print("Building index...")
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
        print("  build")
        print("  load")
        print("  print <word>")
        print('  find <word1> <word2> ...')
        print('  find "phrase query"')
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "load":
        load()

    elif command == "print":
        search = SearchEngine()
        print(search.print_word(sys.argv[2]))

    elif command == "find":
        search = SearchEngine()

        if len(sys.argv) == 3 and " " in sys.argv[2]:
            phrase = sys.argv[2].strip('"')
            words = phrase.split()
            print(search.find_query(words, phrase=True))
        else:
            print(search.find_query(sys.argv[2:]))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
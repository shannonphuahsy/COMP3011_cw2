import sys
from crawler import Crawler
from indexer import InvertedIndex
from search import SearchEngine

# Target website specified in the assignment brief
BASE_URL = "https://quotes.toscrape.com"

# File path for saving and loading the compiled index
INDEX_FILE = "data/index.json"


def build():
    """
    Crawl the target website, build the inverted index,
    and save the resulting index to disk.

    This command:
    - Starts the crawler at BASE_URL
    - Collects page text from all crawled pages
    - Builds the inverted index from the collected pages
    - Persists the index to the filesystem
    """
    print("Building index (this will crawl the website)...")

    crawler = Crawler(BASE_URL)
    pages = crawler.crawl()

    index = InvertedIndex()
    index.build_from_pages(pages)
    index.save(INDEX_FILE)

    print("Index built and saved.")


def load():
    """
    Load a previously built inverted index from disk.

    This command exists to satisfy the explicit 'load'
    requirement in the assignment brief and to demonstrate
    storage and retrieval functionality.
    """
    index = InvertedIndex()
    index.load(INDEX_FILE)
    print("Index loaded successfully.")


def main():
    """
    Entry point for the command-line interface (CLI).

    This function parses user commands and dispatches them
    to the appropriate functionality:
    - build
    - load
    - print
    - find
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/main.py build")
        print("  python src/main.py load")
        print("  python src/main.py print <word>")
        print('  python src/main.py find <word1> <word2> ...')
        print('  python src/main.py find "phrase query"')
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "load":
        load()

    elif command == "print":
        # Print the inverted index entry for a single word
        if len(sys.argv) != 3:
            print("Usage: python src/main.py print <word>")
            return

        search = SearchEngine()
        print(search.print_word(sys.argv[2]))

    elif command == "find":
        # Handle empty queries defensively
        if len(sys.argv) < 3:
            print("Empty query. Please provide search terms.")
            return

        raw_query = sys.argv[2].strip()
        cleaned = raw_query.strip('"').strip()

        if not cleaned:
            print("Empty query. Please provide search terms.")
            return

        words = cleaned.split()

        # Enable phrase search only when the query is quoted
        phrase_mode = raw_query.startswith('"') and len(words) > 1

        search = SearchEngine()
        print(search.find_query(words, phrase=phrase_mode))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
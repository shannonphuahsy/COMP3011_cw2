import sys
from crawler import Crawler
from indexer import InvertedIndex

BASE_URL = "https://quotes.toscrape.com/"
INDEX_FILE = "data/index.json"


def build():
    """
    Crawl the website, build the inverted index, and save it to disk.
    """
    print("Building index (this will crawl the website)...")

    crawler = Crawler(BASE_URL)
    pages = crawler.crawl()

    index = InvertedIndex()
    index.build_from_pages(pages)
    index.save(INDEX_FILE)

    print("Index built and saved.")


def load_index():
    """
    Load the inverted index from disk.
    """
    index = InvertedIndex()
    index.load(INDEX_FILE)
    return index


def print_word(word):
    """
    Print the inverted index entry for a single word.
    """
    index = load_index()
    entry = index.get_word(word)

    if not entry:
        print(f"No results found for '{word}'.")
        return

    print(f"Results for '{word}':")
    for url, data in entry.items():
        print(f"{url} -> count: {data['count']}")


def find_query(words):
    """
    Find pages that contain ALL words in the query (AND search).
    """
    index = load_index()

    # Get sets of pages for each word
    page_sets = []

    for word in words:
        entry = index.get_word(word)
        if not entry:
            print(f"No results found for '{' '.join(words)}'.")
            return
        page_sets.append(set(entry.keys()))

    # AND search using set intersection
    matching_pages = set.intersection(*page_sets)

    if not matching_pages:
        print(f"No pages contain all words: {' '.join(words)}")
        return

    print(f"Pages containing {' '.join(words)}:")
    for page in matching_pages:
        print(page)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/main.py build")
        print("  python src/main.py print <word>")
        print("  python src/main.py find <word1> <word2> ...")
        return

    command = sys.argv[1]

    if command == "build":
        build()

    elif command == "print":
        if len(sys.argv) != 3:
            print("Usage: python src/main.py print <word>")
            return
        print_word(sys.argv[2])

    elif command == "find":
        if len(sys.argv) < 3:
            print("Usage: python src/main.py find <word1> <word2> ...")
            return
        find_query(sys.argv[2:])

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
from indexer import InvertedIndex

INDEX_FILE = "data/index.json"


class SearchEngine:
    """
    Provides search functionality over a loaded inverted index.
    """

    def __init__(self, index_file=INDEX_FILE):
        self.index = InvertedIndex()
        self.index.load(index_file)

    def print_word(self, word):
        """
        Print the inverted index entry for a single word.
        """
        entry = self.index.get_word(word)

        if not entry:
            return f"No results found for '{word}'."

        lines = [f"Results for '{word}':"]
        for url, data in entry.items():
            lines.append(f"{url} -> count: {data['count']}")

        return "\n".join(lines)

    def find_query(self, words):
        """
        Find pages containing ALL words (AND search).
        """
        page_sets = []

        for word in words:
            entry = self.index.get_word(word)
            if not entry:
                return f"No pages contain all words: {' '.join(words)}"
            page_sets.append(set(entry.keys()))

        matching_pages = set.intersection(*page_sets)

        if not matching_pages:
            return f"No pages contain all words: {' '.join(words)}"

        lines = [f"Pages containing {' '.join(words)}:"]
        for page in matching_pages:
            lines.append(page)

        return "\n".join(lines)
import re
from collections import defaultdict


class InvertedIndex:
    """
    Builds and stores an inverted index:
    word -> url -> {count, positions}
    """

    def __init__(self):
        # index[word][url] = {'count': int, 'positions': [int, ...]}
        self.index = defaultdict(lambda: defaultdict(lambda: {
            "count": 0,
            "positions": []
        }))

    def tokenize(self, text):
        """
        Convert text into a list of lowercase tokens.
        Only alphabetic words are kept.
        """
        text = text.lower()
        return re.findall(r"\b[a-z]+\b", text)

    def add_page(self, url, text):
        """
        Add a single page's text to the inverted index.
        """
        tokens = self.tokenize(text)

        for position, word in enumerate(tokens):
            entry = self.index[word][url]
            entry["count"] += 1
            entry["positions"].append(position)

    def build_from_pages(self, pages):
        """
        Build the inverted index from crawled pages.

        :param pages: dict {url: page_text}
        """
        for url, text in pages.items():
            self.add_page(url, text)

    def get_word(self, word):
        """
        Retrieve index entry for a word.
        """
        return self.index.get(word.lower(), {})

    def get_index(self):
        """
        Return the full inverted index.
        """
        return dict(self.index)
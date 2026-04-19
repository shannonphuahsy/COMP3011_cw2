import re
import json
from collections import defaultdict


class InvertedIndex:
    """
    Inverted index:
    word -> url -> {count, positions}
    """

    def __init__(self):
        self.index = defaultdict(lambda: defaultdict(lambda: {
            "count": 0,
            "positions": []
        }))

    def tokenize(self, text):
        text = text.lower()
        return re.findall(r"\b[a-z]+\b", text)

    def add_page(self, url, text):
        tokens = self.tokenize(text)

        for position, word in enumerate(tokens):
            entry = self.index[word][url]
            entry["count"] += 1
            entry["positions"].append(position)

    def build_from_pages(self, pages):
        for url, text in pages.items():
            self.add_page(url, text)

    def get_word(self, word):
        return self.index.get(word.lower(), {})

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.index, f)

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.index = json.load(f)

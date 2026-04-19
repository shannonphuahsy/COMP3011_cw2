import re
import json
import math
from collections import defaultdict
from typing import Dict, List


class InvertedIndex:
    """
    Inverted index structure:

    index[word][url] = {
        "count": int,
        "positions": [int, ...]
    }

    Also stores:
    - document lengths
    - total document count
    """

    def __init__(self):
        self.index = defaultdict(lambda: defaultdict(lambda: {
            "count": 0,
            "positions": []
        }))
        self.doc_lengths: Dict[str, int] = {}
        self.total_docs: int = 0

    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        return re.findall(r"\b[a-z]+\b", text)

    def add_page(self, url: str, text: str) -> None:
        tokens = self.tokenize(text)
        self.doc_lengths[url] = len(tokens)
        self.total_docs += 1

        for position, word in enumerate(tokens):
            entry = self.index[word][url]
            entry["count"] += 1
            entry["positions"].append(position)

    def build_from_pages(self, pages: Dict[str, str]) -> None:
        for url, text in pages.items():
            self.add_page(url, text)

    def get_word(self, word: str) -> Dict:
        return self.index.get(word.lower(), {})

    def idf(self, word: str) -> float:
        df = len(self.get_word(word))
        if df == 0:
            return 0.0
        return math.log(self.total_docs / df)

    def save(self, filepath: str) -> None:
        data = {
            "index": self.index,
            "doc_lengths": self.doc_lengths,
            "total_docs": self.total_docs
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.index = data["index"]
        self.doc_lengths = data["doc_lengths"]
        self.total_docs = data["total_docs"]
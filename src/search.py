from indexer import InvertedIndex
from typing import List, Dict
import time

INDEX_FILE = "data/index.json"


class SearchEngine:
    """
    Search engine supporting:
    - Single-word search
    - Multi-word AND search
    - Phrase search using positional indexing
    - TF-IDF ranking

    AND search complexity: O(sum(df))
    Phrase search complexity: O(sum(df * p))
    """

    def __init__(self, index_file: str = INDEX_FILE):
        self.index = InvertedIndex()
        self.index.load(index_file)

    def print_word(self, word: str) -> str:
        entry = self.index.get_word(word)

        if not entry:
            return f"No results found for '{word}'."

        lines = [f"Results for '{word}':"]
        for url, data in entry.items():
            lines.append(f"{url} -> count: {data['count']}")

        return "\n".join(lines)

    def tf_idf_score(self, word: str, url: str) -> float:
        entry = self.index.get_word(word).get(url)
        if not entry:
            return 0.0

        tf = entry["count"] / self.index.doc_lengths[url]
        idf = self.index.idf(word)
        return tf * idf

    def phrase_match(self, words: List[str], url: str) -> bool:
        """
        Returns True if words occur consecutively in a document.
        """
        positions_lists = [
            self.index.get_word(word)[url]["positions"]
            for word in words
        ]

        first_positions = positions_lists[0]

        for pos in first_positions:
            if all((pos + i) in positions_lists[i] for i in range(1, len(words))):
                return True

        return False

    def find_query(self, words: List[str], phrase: bool = False) -> str:
        """
        Execute AND or phrase query and rank results with TF-IDF.
        Handles empty queries defensively.
        """
        if not words:
            return "Empty query provided. Please enter one or more search terms."

        start_time = time.perf_counter()
        words = [w.lower() for w in words]
        page_sets = []

        for word in words:
            entry = self.index.get_word(word)
            if not entry:
                return f"No pages contain all words: {' '.join(words)}"
            page_sets.append(set(entry.keys()))

        pages = set.intersection(*page_sets)
        if not pages:
            return f"No pages contain all words: {' '.join(words)}"

        if phrase:
            pages = {url for url in pages if self.phrase_match(words, url)}
            if not pages:
                return f"No pages contain the phrase: {' '.join(words)}"

        scored_pages: Dict[str, float] = {}
        for url in pages:
            scored_pages[url] = sum(self.tf_idf_score(word, url) for word in words)

        ranked = sorted(scored_pages.items(), key=lambda x: x[1], reverse=True)
        elapsed = (time.perf_counter() - start_time) * 1000

        lines = [f"Results ({elapsed:.2f} ms):"]
        for url, score in ranked:
            lines.append(f"{url} -> score: {score:.4f}")

        return "\n".join(lines)
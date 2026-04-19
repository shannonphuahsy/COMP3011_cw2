from indexer import InvertedIndex
from typing import List, Dict

INDEX_FILE = "data/index.json"


class SearchEngine:
    """
    Search engine supporting:
    - single-word search
    - multi-word AND search
    - TF-IDF ranking
    - phrase search (optional)
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

    def find_query(self, words: List[str], phrase: bool = False) -> str:
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

        scored_pages: Dict[str, float] = {}

        for url in pages:
            score = sum(self.tf_idf_score(word, url) for word in words)
            scored_pages[url] = score

        ranked = sorted(scored_pages.items(), key=lambda x: x[1], reverse=True)

        lines = [f"Pages containing {' '.join(words)} (ranked):"]
        for url, score in ranked:
            lines.append(f"{url} -> score: {score:.4f}")

        return "\n".join(lines)
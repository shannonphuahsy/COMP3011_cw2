from indexer import InvertedIndex
from typing import List, Dict, Set
import time

# Default file path for the stored inverted index
INDEX_FILE = "data/index.json"


class SearchEngine:
    """
    Search engine providing retrieval functionality over an inverted index.

    Responsibilities:
    - Load a pre-built inverted index from disk
    - Support single-word searches
    - Support multi-word AND queries
    - Support phrase queries using positional indexing
    - Rank search results using TF-IDF
    - Measure and report query execution time

    Design notes:
    - TF-IDF is used to weight relevance
    - Phrase queries are implemented as a positional intersection
    - Empty and invalid queries are handled defensively
    """

    def __init__(self, index_file: str = INDEX_FILE):
        """
        Initialise the search engine by loading the inverted index.

        Args:
            index_file (str): Path to the index file on disk.
        """
        self.index = InvertedIndex()
        self.index.load(index_file)

    def print_word(self, word: str) -> str:
        """
        Print the inverted index entry for a single word.

        This command displays all documents containing the word,
        along with the frequency of occurrence in each document.

        Args:
            word (str): Query word.

        Returns:
            str: Formatted string representation of the inverted index entry.
        """
        entry = self.index.get_word(word)

        if not entry:
            return f"No results found for '{word}'."

        lines = [f"Results for '{word}:"]
        for url, data in entry.items():
            lines.append(f"{url} -> count: {data['count']}")

        return "\n".join(lines)

    def tf_idf_score(self, word: str, url: str) -> float:
        """
        Compute the TF-IDF relevance score for a word in a document.

        TF (Term Frequency):
            count(word, document) / document_length

        IDF (Inverse Document Frequency):
            log(total_documents / document_frequency)

        Args:
            word (str): Query term.
            url (str): Document identifier.

        Returns:
            float: TF-IDF score.
        """
        entry = self.index.get_word(word).get(url)
        if not entry:
            return 0.0

        tf = entry["count"] / self.index.doc_lengths[url]
        idf = self.index.idf(word)

        return tf * idf

    def phrase_match(self, words: List[str], url: str) -> bool:
        """
        Determine whether a phrase occurs consecutively in a document.

        Uses positional indexing:
        - Checks whether adjacent terms appear at successive positions.

        Args:
            words (List[str]): Phrase split into individual words.
            url (str): Document identifier.

        Returns:
            bool: True if the phrase occurs in the document, False otherwise.
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

    def find_and_query(self, words: List[str]) -> Set[str]:
        """
        Perform a Boolean AND query over the indexed documents.

        Args:
            words (List[str]): Query terms.

        Returns:
            Set[str]: Set of document URLs containing all query terms.
        """
        page_sets = []

        for word in words:
            entry = self.index.get_word(word)
            if not entry:
                return set()
            page_sets.append(set(entry.keys()))

        return set.intersection(*page_sets)

    def find_query(self, words: List[str], phrase: bool = False) -> str:
        """
        Execute a search query and return ranked results.

        The method supports:
        - AND queries (default): finds documents containing all words
        - Phrase queries: finds documents containing the exact phrase

        Results are ranked using TF-IDF and returned with
        execution time for benchmarking.

        Args:
            words (List[str]): Search terms.
            phrase (bool): Whether to enable phrase search mode.

        Returns:
            str: Formatted string containing ranked search results.
        """
        if not words:
            return "Empty query provided. Please enter one or more search terms."

        start_time = time.perf_counter()
        words = [w.lower() for w in words]

        # Step 1: Boolean AND filtering
        pages = self.find_and_query(words)
        if not pages:
            return f"No pages contain all words: {' '.join(words)}"

        # Step 2: Optional phrase filtering
        if phrase:
            pages = {url for url in pages if self.phrase_match(words, url)}
            if not pages:
                return f"No pages contain the phrase: {' '.join(words)}"

        # Step 3: TF-IDF ranking
        scored_pages: Dict[str, float] = {}
        for url in pages:
            scored_pages[url] = sum(
                self.tf_idf_score(word, url) for word in words
            )

        ranked = sorted(scored_pages.items(), key=lambda x: x[1], reverse=True)

        elapsed = (time.perf_counter() - start_time) * 1000

        # Step 4: Format output
        lines = [f"Results ({elapsed:.2f} ms):"]
        for url, score in ranked:
            lines.append(f"{url} -> score: {score:.4f}")

        return "\n".join(lines)
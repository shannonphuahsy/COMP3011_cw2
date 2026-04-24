import re
import json
import math
import time
from collections import defaultdict
from typing import Dict, List


class InvertedIndex:
    """
    Inverted index for a collection of crawled web pages.

    Responsibilities:
    - Tokenise page text into individual terms
    - Build an inverted index mapping words to documents
    - Store term statistics such as frequency and positional information
    - Support TF-IDF weighting through document statistics
    - Persist and reload the index from disk

    Index structure:
        index[word][url] = {
            "count": int,        # term frequency in the document
            "positions": List[int]  # positions of the term in the document
        }

    Additional metadata:
    - doc_lengths[url] = total number of tokens in the document
    - total_docs = total number of indexed documents
    """

    def __init__(self):
        """
        Initialise an empty inverted index.
        """
        # Main inverted index structure
        self.index = defaultdict(lambda: defaultdict(lambda: {
            "count": 0,
            "positions": []
        }))

        # Stores the number of tokens per document
        self.doc_lengths: Dict[str, int] = {}

        # Total number of indexed documents
        self.total_docs: int = 0

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenise input text into lowercase alphabetic terms.

        This implementation:
        - Converts text to lowercase
        - Extracts contiguous alphabetic words using regular expressions
        - Ignores numbers, punctuation, and special characters

        Args:
            text (str): Raw text extracted from a web page.

        Returns:
            List[str]: List of normalised word tokens.
        """
        text = text.lower()
        return re.findall(r"\b[a-z]+\b", text)

    def add_page(self, url: str, text: str) -> None:
        """
        Add a single page to the inverted index.

        This method:
        - Tokenises the page text
        - Records the document length
        - Updates term frequency and positional information for each token

        Args:
            url (str): URL of the page being indexed.
            text (str): Clean visible text extracted from the page.
        """
        tokens = self.tokenize(text)

        # Record document length (used for TF normalisation)
        self.doc_lengths[url] = len(tokens)
        self.total_docs += 1

        # Populate inverted index with token statistics
        for position, word in enumerate(tokens):
            entry = self.index[word][url]
            entry["count"] += 1
            entry["positions"].append(position)

    def build_from_pages(self, pages: Dict[str, str]) -> None:
        """
        Build the inverted index from a collection of crawled pages.

        This function iterates through all pages returned by the crawler
        and indexes them sequentially. Indexing performance is tracked
        for benchmarking purposes.

        Args:
            pages (Dict[str, str]): Mapping of URL -> page text.
        """
        start = time.perf_counter()

        for url, text in pages.items():
            self.add_page(url, text)

        elapsed = time.perf_counter() - start
        print(f"Indexed {self.total_docs} documents in {elapsed:.2f}s")

    def get_word(self, word: str) -> Dict:
        """
        Retrieve the inverted index entry for a given word.

        Args:
            word (str): Query term.

        Returns:
            Dict: Mapping of URL -> term statistics for the given word.
                  Returns an empty dictionary if the word is not indexed.
        """
        return self.index.get(word.lower(), {})

    def idf(self, word: str) -> float:
        """
        Compute the Inverse Document Frequency (IDF) of a term.

        IDF formula:
            idf = log(total_documents / document_frequency)

        Terms that appear in all documents receive an IDF of 0,
        reflecting their low discriminative power.

        Args:
            word (str): Query term.

        Returns:
            float: IDF score for the term.
        """
        df = len(self.get_word(word))
        if df == 0:
            return 0.0
        return math.log(self.total_docs / df)

    def save(self, filepath: str) -> None:
        """
        Save the inverted index and associated metadata to disk.

        Args:
            filepath (str): Path of the file to save the index to.
        """
        data = {
            "index": self.index,
            "doc_lengths": self.doc_lengths,
            "total_docs": self.total_docs
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, filepath: str) -> None:
        """
        Load a previously saved inverted index from disk.

        Args:
            filepath (str): Path of the file containing the saved index.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.index = data["index"]
        self.doc_lengths = data["doc_lengths"]
        self.total_docs = data["total_docs"]
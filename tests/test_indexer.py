import sys
from pathlib import Path
import math

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indexer import InvertedIndex


# =========================
# Tokenisation tests
# =========================

def test_tokenisation_is_case_insensitive():
    """
    Tokenisation should normalise all tokens to lowercase.
    """
    index = InvertedIndex()
    tokens = index.tokenize("Life LIFE life")

    assert tokens == ["life", "life", "life"]


def test_tokenisation_removes_punctuation():
    """
    Tokenisation should remove punctuation and extract
    only alphabetic tokens.
    """
    index = InvertedIndex()
    tokens = index.tokenize("life, life! life?")

    assert tokens == ["life", "life", "life"]


# =========================
# Index construction tests
# =========================

def test_word_counts_and_positions():
    """
    The inverted index should correctly record
    term frequency and positions.
    """
    index = InvertedIndex()
    index.add_page("page1", "life is life")

    entry = index.get_word("life")["page1"]

    assert entry["count"] == 2
    assert entry["positions"] == [0, 2]


def test_document_lengths_and_total_docs_tracked():
    """
    The index should track document lengths
    and the total number of documents.
    """
    index = InvertedIndex()

    index.add_page("page1", "one two")
    index.add_page("page2", "three four five")

    assert index.doc_lengths["page1"] == 2
    assert index.doc_lengths["page2"] == 3
    assert index.total_docs == 2


def test_missing_word_returns_empty_dict():
    """
    Querying a word not present in the index
    should return an empty dictionary.
    """
    index = InvertedIndex()
    index.add_page("page1", "life is good")

    assert index.get_word("missing") == {}


# =========================
# Statistical tests
# =========================

def test_idf_calculation_matches_definition():
    """
    IDF(word) = log(total_documents / document_frequency)

    When a word appears in all documents,
    its inverse document frequency should be zero.
    """
    index = InvertedIndex()

    index.add_page("p1", "life is good")
    index.add_page("p2", "life is short")

    expected_idf = math.log(2 / 2)
    assert math.isclose(index.idf("life"), expected_idf)
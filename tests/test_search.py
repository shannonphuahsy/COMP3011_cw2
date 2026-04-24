import sys
from pathlib import Path
import json
import os

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from search import SearchEngine

# Temporary index file used for deterministic search tests
TEST_INDEX_FILE = "tests/test_index.json"


# =========================
# Setup / teardown
# =========================

def setup_module(module):
    """
    Create a deterministic inverted index for testing search behaviour.

    Design:
    - 'unique' appears in only one document (non-zero IDF, clear ranking)
    - 'life' appears in multiple documents
    - positional information enables phrase testing
    """
    index_data = {
        "index": {
            "unique": {
                "page1": {"count": 3, "positions": [0, 1, 2]}
            },
            "life": {
                "page1": {"count": 3, "positions": [0, 1, 2]},
                "page2": {"count": 1, "positions": [10]}
            },
            "good": {
                "page1": {"count": 1, "positions": [5]}
            },
            "friends": {
                "page1": {"count": 1, "positions": [6]},
                "page2": {"count": 1, "positions": [20]}
            }
        },
        "doc_lengths": {
            "page1": 10,
            "page2": 25
        },
        "total_docs": 2
    }

    with open(TEST_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f)


def teardown_module(module):
    """
    Remove the temporary index file after tests complete.
    """
    if os.path.exists(TEST_INDEX_FILE):
        os.remove(TEST_INDEX_FILE)


# =========================
# Print command tests
# =========================

def test_print_existing_word():
    """
    print_word should list all documents containing the word.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("life")

    assert "page1" in output
    assert "page2" in output


def test_print_missing_word():
    """
    print_word should return a clear message if the word is not indexed.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("missing")

    assert "No results found" in output


# =========================
# AND query tests
# =========================

def test_and_query_returns_documents_containing_all_terms():
    """
    AND search should return only documents that contain all terms.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "unique"])

    assert "page1" in output
    assert "page2" not in output


def test_and_query_missing_term_returns_message():
    """
    AND search should fail cleanly if one term is missing.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "missing"])

    assert "No pages contain all words" in output


# =========================
# Ranking (TF-IDF) tests
# =========================

def test_ranked_results_are_ordered_by_relevance():
    """
    Queries with non-zero IDF should produce ranked results.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["unique"])

    lines = output.splitlines()

    # page1 should be the top-ranked (and only) result
    assert "page1" in lines[1]
    assert "page2" not in output


# =========================
# Phrase query tests
# =========================

def test_phrase_query_returns_only_exact_phrase_matches():
    """
    Phrase search should match only documents where
    words appear consecutively.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["good", "friends"], phrase=True)

    assert "page1" in output
    assert "page2" not in output


def test_phrase_query_no_match_returns_message():
    """
    Phrase query should fail cleanly if the phrase does not occur.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "friends"], phrase=True)

    assert "No pages contain the phrase" in output


# =========================
# Input validation tests
# =========================

def test_empty_query_returns_clear_message():
    """
    Empty queries should be handled defensively.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query([])

    assert "Empty query" in output
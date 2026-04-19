import sys
from pathlib import Path
import json
import os

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from search import SearchEngine

TEST_INDEX_FILE = "tests/test_index.json"


# =========================
# Setup / teardown
# =========================

def setup_module(module):
    """
    Create a deterministic index file where TF-IDF
    produces a meaningful ordering.
    """
    index_data = {
        "index": {
            "unique": {
                "page1": {"count": 3, "positions": [0, 1, 2]}
            },
            "life": {
                "page1": {"count": 3, "positions": [0, 1, 2]},
                "page2": {"count": 1, "positions": [10]}
            }
        },
        "doc_lengths": {
            "page1": 4,
            "page2": 12
        },
        "total_docs": 2
    }

    with open(TEST_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f)


def teardown_module(module):
    if os.path.exists(TEST_INDEX_FILE):
        os.remove(TEST_INDEX_FILE)


# =========================
# Print command tests
# =========================

def test_print_existing_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("life")

    assert "page1" in output
    assert "page2" in output


def test_print_missing_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("missing")

    assert "No results found" in output


# =========================
# Ranking / TF-IDF tests
# =========================

def test_ranked_results_are_ordered_by_relevance():
    """
    'unique' appears in only one document,
    so its IDF is non-zero and ranking is meaningful.
    """
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["unique"])

    lines = output.splitlines()

    assert "page1" in lines[1]
    assert "page2" not in output


def test_and_query_filters_documents_correctly():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "unique"])

    assert "page1" in output
    assert "page2" not in output


def test_missing_query_term_returns_clear_message():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "missing"])

    assert "No pages contain all words" in output
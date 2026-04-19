import json
import os
from src.search import SearchEngine

TEST_INDEX_FILE = "tests/test_index.json"


def setup_module():
    test_index = {
        "life": {
            "page1": {"count": 2, "positions": [0, 3]},
            "page2": {"count": 1, "positions": [5]}
        },
        "good": {
            "page1": {"count": 1, "positions": [2]}
        }
    }

    with open(TEST_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(test_index, f)


def teardown_module():
    if os.path.exists(TEST_INDEX_FILE):
        os.remove(TEST_INDEX_FILE)


def test_print_existing_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("life")

    assert "page1" in output
    assert "page2" in output


def test_print_missing_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.print_word("missing")

    assert "No results found" in output


def test_find_single_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life"])

    assert "page1" in output
    assert "page2" in output


def test_find_multiple_words_and_search():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "good"])

    assert "page1" in output
    assert "page2" not in output


def test_find_missing_word():
    search = SearchEngine(TEST_INDEX_FILE)
    output = search.find_query(["life", "missing"])

    assert "No pages contain all words" in output
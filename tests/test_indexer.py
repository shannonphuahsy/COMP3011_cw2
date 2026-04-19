import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indexer import InvertedIndex


def test_tokenization_is_case_insensitive_and_clean():
    index = InvertedIndex()
    text = "Life, LIFE! life?"
    tokens = index.tokenize(text)

    assert tokens == ["life", "life", "life"]


def test_add_page_records_word_counts_and_positions():
    index = InvertedIndex()
    index.add_page("page1", "Life is life")

    entry = index.get_word("life")["page1"]

    assert entry["count"] == 2
    assert entry["positions"] == [0, 2]


def test_document_length_and_total_docs_tracked():
    index = InvertedIndex()

    index.add_page("page1", "one two")
    index.add_page("page2", "three four five")

    assert index.doc_lengths["page1"] == 2
    assert index.doc_lengths["page2"] == 3
    assert index.total_docs == 2


def test_missing_word_returns_empty_dict():
    index = InvertedIndex()
    index.add_page("page1", "life is good")

    assert index.get_word("missing") == {}


def test_idf_computation_matches_definition():
    index = InvertedIndex()

    index.add_page("page1", "life is good")
    index.add_page("page2", "life is short")

    expected_idf = math.log(2 / 2)
    assert math.isclose(index.idf("life"), expected_idf)
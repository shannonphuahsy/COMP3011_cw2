import pytest
from src.indexer import InvertedIndex


def test_tokenisation_basic():
    index = InvertedIndex()
    text = "Life is Good. Life is beautiful!"
    tokens = index.tokenize(text)

    assert tokens == ["life", "is", "good", "life", "is", "beautiful"]


def test_add_page_counts_words_correctly():
    index = InvertedIndex()
    index.add_page("page1", "Life is good. Life is short.")

    result = index.get_word("life")
    assert "page1" in result
    assert result["page1"]["count"] == 2


def test_case_insensitivity():
    index = InvertedIndex()
    index.add_page("page1", "Life life LIFE")

    result = index.get_word("life")
    assert result["page1"]["count"] == 3


def test_positions_are_recorded():
    index = InvertedIndex()
    index.add_page("page1", "Life is life")

    result = index.get_word("life")
    assert result["page1"]["positions"] == [0, 2]


def test_missing_word_returns_empty():
    index = InvertedIndex()
    index.add_page("page1", "Life is good")

    assert index.get_word("missing") == {}
from contextlib import contextmanager

import pytest

import rag.semantic_search as semantic_search
from rag.semantic_search import SemanticSearchEngine


class FakeResult:
    def __init__(self, name):
        self.name = name


class FakeModel:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, query):
        assert query == "algebra"
        return type("Emb", (), {"tolist": lambda self: [0.1, 0.2, 0.3]})()


class FakeDBRow:
    def mappings(self):
        return self

    def all(self):
        return [FakeResult("Algorytmy i struktury danych")]


class FakeDB:
    def __init__(self):
        self.statements = []

    def execute(self, statement, params):
        self.statements.append((str(statement), params))
        return FakeDBRow()


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setattr(semantic_search, "SentenceTransformer", FakeModel)
    return SemanticSearchEngine()


def test_search_returns_results(engine, monkeypatch):
    fake_db = FakeDB()

    @contextmanager
    def fake_get_db(commit=False):
        yield fake_db

    monkeypatch.setattr(semantic_search, "get_db", fake_get_db)
    results = engine.search("algebra")
    assert len(results) == 1
    assert results[0].name == "Algorytmy i struktury danych"


def test_search_uses_query_embedding_in_query(engine, monkeypatch):
    fake_db = FakeDB()

    @contextmanager
    def fake_get_db(commit=False):
        yield fake_db

    monkeypatch.setattr(semantic_search, "get_db", fake_get_db)
    engine.search("algebra")
    statement, params = fake_db.statements[0]
    assert "course_data" in statement
    assert params["embedding"] == [0.1, 0.2, 0.3]
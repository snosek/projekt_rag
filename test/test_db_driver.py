import pytest

import rag.db_driver


class FakeDB:
    def __init__(self):
        self.committed = False
        self.closed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True

    def rollback(self):
        self.rolled_back = True

    def execute(self, *args, **kwargs):
        return None


@pytest.fixture
def fake_db(monkeypatch):
    fake = FakeDB()
    monkeypatch.setattr(rag.db_driver, "session", lambda: fake)
    return fake


def test_get_db_yields_session_and_closes(fake_db):
    yielded = None
    with rag.db_driver.get_db() as db:
        yielded = db
    assert yielded is fake_db
    assert fake_db.closed
    assert not fake_db.committed


def test_get_db_commits_when_requested(fake_db):
    with rag.db_driver.get_db(commit=True) as db:
        db.execute("SELECT 1")
    assert fake_db.committed
    assert fake_db.closed


def test_get_db_rolls_back_on_exception(fake_db):
    with pytest.raises(RuntimeError, match="boom"):
        with rag.db_driver.get_db() as db:
            raise RuntimeError("boom")
    assert fake_db.rolled_back
    assert fake_db.closed
    assert not fake_db.committed
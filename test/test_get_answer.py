import pytest

import rag.chatbot as chatbot
from rag.chatbot import get_answer


class FakeContent:
    def __init__(self, text):
        self.text = text


class FakeMessage:
    def __init__(self, text):
        self.content = [FakeContent(text)]


class FakeResponse:
    def __init__(self, text):
        self.message = FakeMessage(text)


def test_get_answer_returns_cohere_text(monkeypatch):
    def fake_client():
        class FakeCohere:
            def chat(self, **kwargs):
                assert kwargs["model"] == "command-a-plus-05-2026"
                assert kwargs["messages"][0]["role"] == "user"
                return FakeResponse("To jest odpowiedz.")

        return FakeCohere()

    monkeypatch.setattr(chatbot, "get_client", fake_client)
    assert get_answer("prompt") == "To jest odpowiedz."


def test_get_answer_raises_on_empty_content(monkeypatch):
    class EmptyMessage:
        def __init__(self):
            self.content = []

    class EmptyResponse:
        def __init__(self):
            self.message = EmptyMessage()

    def fake_client():
        class FakeCohere:
            def chat(self, **kwargs):
                return EmptyResponse()

        return FakeCohere()

    monkeypatch.setattr(chatbot, "get_client", fake_client)
    with pytest.raises(RuntimeError, match="empty"):
        get_answer("prompt")

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
    def fake_chat(**kwargs):
        assert kwargs["model"] == "command-a-plus-05-2026"
        assert kwargs["messages"][0]["role"] == "user"
        return FakeResponse("To jest odpowiedz.")

    monkeypatch.setattr(chatbot.co, "chat", fake_chat)
    assert get_answer("prompt") == "To jest odpowiedz."
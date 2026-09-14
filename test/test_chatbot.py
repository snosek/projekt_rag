import pytest

from rag.chatbot import create_prompt


def make_course(**overrides):
    data = {
        "Nazwa w języku polskim": "Wprowadzenie do programowania",
        "ECTS": "5",
        "Język prowadzenia zajęć": "polski",
        "Jednostka prowadząca": "Wydział Informatyki",
        "Kierownik przedmiotu": "dr inż. Jan Kowalski",
        "Wymagania wstępne": "Podstawy informatyki",
        "Przedmiotowe efekty uczenia się": "Student zna pętle i funkcje",
        "Metody weryfikacji przedmiotowych efektów uczenia się": "kolokwium",
        "Kierunkowe efekty uczenia się": "K1_W01",
        "Formy i warunki zaliczenia przedmiotu": "zaliczenie z oceną",
        "Szczegółowe treści przedmiotu": "Zmienne, wyrażenia, sterowanie",
    }
    data.update(overrides)
    return {"data": data}


def test_prompt_contains_query():
    prompt = create_prompt("ile punktów ECTS", [make_course()])
    assert "ile punktów ECTS" in prompt


def test_prompt_contains_all_course_fields():
    course = make_course()
    prompt = create_prompt("pytanie", [course])
    for _, value in course["data"].items():
        assert value in prompt


def test_prompt_contains_multiple_courses():
    c1 = make_course(ECTS="5")
    c2 = make_course(ECTS="7", **{"Nazwa w języku polskim": "Algebra"})
    prompt = create_prompt("pytanie", [c1, c2])
    assert "ECTS: 5" in prompt
    assert "ECTS: 7" in prompt
    assert "Algebra" in prompt


def test_prompt_empty_courses():
    prompt = create_prompt("pytanie", [])
    assert "Kurs o nazwie:" not in prompt
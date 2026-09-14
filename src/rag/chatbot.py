from __future__ import annotations

import cohere

from rag.config import COHERE_MODEL
from rag.course_fields import (
    COURSE_CONTENT,
    COURSE_LANGUAGE,
    COURSE_LEADER,
    COURSE_NAME,
    ECTS,
    ORGANIZING_UNIT,
    OUTCOME_VERIFICATION_METHODS,
    PASS_CONDITIONS,
    PREREQUISITES,
    PROGRAM_LEARNING_OUTCOMES,
    SUBJECT_LEARNING_OUTCOMES,
)

_cohere_client: cohere.ClientV2 | None = None


def get_client() -> cohere.ClientV2:
    global _cohere_client
    if _cohere_client is None:
        _cohere_client = cohere.ClientV2()
    return _cohere_client


def create_prompt(query: str, closest_courses: list[dict]) -> str:
    course_text = "\n\n".join(
        [
            f"Kurs o nazwie: {course['data'][COURSE_NAME]}\n"
            f"ECTS: {course['data'][ECTS]}\n"
            f"Język prowadzenia zajęć: {course['data'][COURSE_LANGUAGE]}\n"
            f"Jednostka prowadząca: {course['data'][ORGANIZING_UNIT]}\n"
            f"Kierownik przedmiotu: {course['data'][COURSE_LEADER]}\n"
            f"Wymagania wstępne: {course['data'][PREREQUISITES]}\n"
            f"Przedmiotowe efekty uczenia się: {course['data'][SUBJECT_LEARNING_OUTCOMES]}\n"
            f"Metody weryfikacji efektów uczenia się: {course['data'][OUTCOME_VERIFICATION_METHODS]}\n"
            f"Kierunkowe efekty uczenia się: {course['data'][PROGRAM_LEARNING_OUTCOMES]}\n"
            f"Formy i warunki zaliczenia przedmiotu: {course['data'][PASS_CONDITIONS]}\n"
            f"Szczegółowe treści przedmiotu: {course['data'][COURSE_CONTENT]}\n"
            for course in closest_courses
        ]
    )
    prompt = f"""
    Wciel się w role systemu z wiedzą domenową z zakresu kursów na Politechnice Łódzkiej. Otrzymujesz następujące zapytanie:
    {query}.
    Bazując jedynie na poniższych opisach kursów podanych w języku polskim, odpowiedz na to pytanie.
    Podaj tylko odpowiedź, nie używaj narzędzi formatujących. Jeśli to możliwe, unikaj punktorów i numeracji.
    Jednym zdaniem opisz każdy z wyników.
    Oto kursy związane z zadanym pytaniem:
    {course_text}
    """
    return prompt


def get_answer(prompt: str) -> str:
    response = get_client().chat(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model=COHERE_MODEL,
    )
    if not response.message.content:
        raise RuntimeError("Cohere returned an empty response.")
    return response.message.content[-1].text

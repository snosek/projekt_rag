from os import getenv
from dotenv import load_dotenv
import cohere
import logging as log

log.info("Loading .env...")
load_dotenv()

ENV_VAR_NAMES = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_PORT"]

log.info(f'''.env loaded: {
        [getenv(name) for name in ENV_VAR_NAMES]
    }'''
)

def create_prompt(query, closest_courses):
    course_text = "\n\n".join(
        [
            f"Kurs o nazwie: {course['data']['Nazwa w języku polskim']}\n"
            f"ECTS: {course['data']['ECTS']}\n"
            f"Język prowadzenia zajęć: {course['data']['Język prowadzenia zajęć']}\n"
            f"Jednostka prowadząca: {course['data']['Jednostka prowadząca']}\n"
            f"Kierownik przedmiotu: {course['data']['Kierownik przedmiotu']}\n"
            f"Wymagania wstępne: {course['data']['Wymagania wstępne']}\n"
            f"Przedmiotowe efekty uczenia się: {course['data']['Przedmiotowe efekty uczenia się']}\n"
            f"Metody weryfikacji efektów uczenia się: {course['data']['Metody weryfikacji przedmiotowych efektów uczenia się']}\n"
            f"Kierunkowe efekty uczenia się: {course['data']['Kierunkowe efekty uczenia się']}\n"
            f"Formy i warunki zaliczenia przedmiotu: {course['data']['Formy i warunki zaliczenia przedmiotu']}\n"
            f"Szczegółowe treści przedmiotu: {course['data']['Szczegółowe treści przedmiotu']}\n"
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

co = cohere.ClientV2()

def get_answer(prompt):
    response = co.chat(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="command-a-plus-05-2026",
    )
    return response.message.content[-1].text

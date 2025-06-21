from os import getenv
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=getenv("GROQ_API_KEY")
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

def get_answer(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

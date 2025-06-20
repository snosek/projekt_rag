from sqlalchemy import text
from sentence_transformers import SentenceTransformer
from rag.db_driver import get_db

def main():
    populate_db_with_embeddings()

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def populate_db_with_embeddings():
    with get_db() as db:
        docs = db.execute(text("SELECT * from course_data;")).mappings().all()
    for doc in [dict(d) for d in docs]:
        row_id = doc["id"]
        doc = doc["data"]
        course_name = doc["Nazwa w języku polskim"]
        course_requirements = doc["Wymagania wstępne"]
        course_effects = doc["Kierunkowe efekty uczenia się"]
        course_desc = doc["Szczegółowe treści przedmiotu"]
        course_ects = doc["ECTS"]
        course_leader = doc["Kierownik przedmiotu"]
        description = ". ".join(
            [
                f"Przedmiot nosi nazwę: {course_name}",
                f"Aby do niego przystąpić wymagana jest wiedza z: {course_requirements}",
                f"Kurs pozwala osiągnąć następujące efekty: {course_effects}",
                f"Można go opisać w następujący sposób: {course_desc}",
                f"Przypisane do niego jest {course_ects} ECTS",
                f"Prowadzi go {course_leader}",
            ]
        )
        embedding = model.encode([description]).reshape(1, -1).tolist()[0]
        with get_db(commit=True) as db:
            db.execute(
                text(
                    """UPDATE course_data
                    SET embedding = :embedding
                    WHERE id = :id """
                ),
                {"embedding": embedding, "id": row_id},
            )

if __name__ == "__main__":
    main()
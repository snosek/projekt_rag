from sentence_transformers import SentenceTransformer

from rag.config import EMBEDDING_MODEL
from rag.course_fields import (
    COURSE_CONTENT,
    COURSE_LEADER,
    COURSE_NAME,
    ECTS,
    PREREQUISITES,
    PROGRAM_LEARNING_OUTCOMES,
)
from rag.repository import CourseRepository


def build_description(data: dict) -> str:
    course_name = data[COURSE_NAME]
    course_requirements = data[PREREQUISITES]
    course_effects = data[PROGRAM_LEARNING_OUTCOMES]
    course_desc = data[COURSE_CONTENT]
    course_ects = data[ECTS]
    course_leader = data[COURSE_LEADER]
    return ". ".join(
        [
            f"Przedmiot nosi nazwę: {course_name}",
            f"Aby do niego przystąpić wymagana jest wiedza z: {course_requirements}",
            f"Kurs pozwala osiągnąć następujące efekty: {course_effects}",
            f"Można go opisać w następujący sposób: {course_desc}",
            f"Przypisane do niego jest {course_ects} ECTS",
            f"Prowadzi go {course_leader}",
        ]
    )


def populate_db_with_embeddings(repository: CourseRepository, model: SentenceTransformer):
    rows = repository.all()
    entries = []
    for row in rows:
        description = build_description(row["data"])
        embedding = model.encode([description]).reshape(1, -1).tolist()[0]
        entries.append({"id": row["id"], "embedding": embedding})
    repository.update_embeddings(entries)


def main():
    model = SentenceTransformer(EMBEDDING_MODEL)
    populate_db_with_embeddings(CourseRepository(), model)


if __name__ == "__main__":
    main()

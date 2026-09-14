from sqlalchemy import text

from rag.config import EMBEDDING_DIM
from rag.db_driver import get_db


class CourseRepository:
    def create_schema(self) -> None:
        with get_db(commit=True) as db:
            db.execute(text("DROP TABLE IF EXISTS course_data;"))
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.execute(
                text(
                    f"""CREATE TABLE IF NOT EXISTS course_data
                    (id SERIAL PRIMARY KEY, data JSONB, embedding VECTOR({EMBEDDING_DIM}));"""
                )
            )

    def insert(self, data: str) -> None:
        with get_db(commit=True) as db:
            db.execute(
                text("INSERT INTO course_data (data) VALUES (:data)"), {"data": data}
            )

    def all(self) -> list:
        with get_db() as db:
            return db.execute(text("SELECT * FROM course_data;")).mappings().all()

    def update_embeddings(self, entries: list[dict]) -> None:
        with get_db(commit=True) as db:
            for entry in entries:
                db.execute(
                    text(
                        "UPDATE course_data SET embedding = :embedding WHERE id = :id"
                    ),
                    entry,
                )

    def semantic_search(self, embedding: list, limit: int) -> list:
        with get_db() as db:
            return (
                db.execute(
                    text(
                        """
                        SELECT data FROM course_data
                        ORDER BY embedding <=> CAST(:embedding AS vector)
                        LIMIT :limit;
                        """
                    ),
                    {"embedding": embedding, "limit": limit},
                ).mappings().all()
            )
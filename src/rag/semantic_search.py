from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from rag.db_driver import get_db


class SemanticSearchEngine:
    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu",
        )

    def search(self, query: str) -> list:
        embedding = self.model.encode(query)
        with get_db() as db:
            results = db.execute(
                text(
                    """
                    SELECT data FROM course_data
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 10;
                """
                ),
                {"embedding": embedding.tolist()},
            ).mappings().all()
        return results

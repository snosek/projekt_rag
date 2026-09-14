from sentence_transformers import SentenceTransformer

from rag.config import EMBEDDING_MODEL, SEMANTIC_SEARCH_LIMIT
from rag.repository import CourseRepository


class SemanticSearchEngine:
    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        limit: int = SEMANTIC_SEARCH_LIMIT,
    ) -> None:
        self.model = SentenceTransformer(model_name, device="cpu")
        self._repository = CourseRepository()
        self.limit = limit

    def search(self, query: str) -> list:
        embedding = self.model.encode(query)
        return self._repository.semantic_search(embedding.tolist(), self.limit)

from os import getenv

from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = getenv("POSTGRES_DB", "postgres")

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

SEMANTIC_SEARCH_LIMIT = 10

COHERE_MODEL = getenv("COHERE_MODEL", "command-a-plus-05-2026")
COURSE_DATA_DIR = getenv("COURSE_DATA_DIR", "data/dane_low_level")
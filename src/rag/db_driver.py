from contextlib import contextmanager

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from rag.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

conn_url = URL.create(
    drivername="postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
)
engine = create_engine(conn_url)
session = sessionmaker(bind=engine, autoflush=False)


@contextmanager
def get_db(commit: bool = False):
    """
    Usage:
        >>> with get_db() as db:
        ...     version = db.execute(text("SELECT version();")).all()
    """
    db = session()
    try:
        yield db
        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

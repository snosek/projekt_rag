from os import getenv
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

conn_url = URL.create(
    drivername="postgresql+psycopg2",
    username=getenv("POSTGRES_USER"),
    password=getenv("POSTGRES_PASSWORD"),
    host="postgres",
    port=getenv("POSTGRES_PORT"),
    database=getenv("POSTGRES_DB"),
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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        if commit:
            db.commit()
        db.close()

from argparse import ArgumentParser, BooleanOptionalAction
import json
from pathlib import Path
from sqlalchemy import text
from src.rag.drivers.db_driver import get_db


def main():
    args = parse_args()
    if args.init:
        create_schema()
    if args.populate:
        populate_db()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--init",
        action=BooleanOptionalAction,
        help="whether to init db schema",
    )
    parser.add_argument(
        "--populate",
        action=BooleanOptionalAction,
        help="whether to populate db with course data",
    )
    return parser.parse_args()


def create_schema():
    print("running create_schema")
    with get_db(commit=True) as db:
        db.execute(text("DROP TABLE IF EXISTS course_data;"))
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.execute(
            text(
                """CREATE TABLE IF NOT EXISTS course_data 
                (id SERIAL PRIMARY KEY,data JSONB,embedding VECTOR(384));"""
            )
        )


def populate_db():
    print("running populate_db")
    courses_dir = "data/dane_low_level"
    courses_dir = Path("data/dane_low_level")
    json_filepaths = courses_dir.glob("*.json")
    for filepath in json_filepaths:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.dumps(json.load(f))
            except json.JSONDecodeError as e:
                print(f"Failed to load {filepath}: {e}")
                continue
        with get_db(commit=True) as db:
            db.execute(
                text("INSERT INTO course_data (data) VALUES (:data)"), {"data": data}
            )


if __name__ == "__main__":
    main()

import json
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from rag.config import COURSE_DATA_DIR
from rag.repository import CourseRepository


def main():
    args = parse_args()
    repository = CourseRepository()
    if args.init:
        repository.create_schema()
    if args.populate:
        populate_db(repository)


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


def populate_db(repository: CourseRepository):
    json_filepaths = Path(COURSE_DATA_DIR).glob("*.json")
    for filepath in json_filepaths:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.dumps(json.load(f))
            except json.JSONDecodeError as e:
                print(f"Failed to load {filepath}: {e}")
                continue
        repository.insert(data)


if __name__ == "__main__":
    main()

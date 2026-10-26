import sqlite3
from collections.abc import Generator
from pathlib import Path
import os

DATABASE_PATH = Path(
    os.environ.get(
        "TASKS_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "tasks.db"),
    )
)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

import os
import sqlite3
from pathlib import Path
from typing import Optional

path = Path(os.path.dirname(__file__))
DATABASE_PATH = path.parent / "db/chinook.db"


class SqlLocalDatabaseContextManager:
    def __init__(self, database_file_path=DATABASE_PATH):
        self.database_file_path = database_file_path
        self.con: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Cursor:
        self.con = sqlite3.connect(self.database_file_path)
        return self.con.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con is not None:
            self.con.close()

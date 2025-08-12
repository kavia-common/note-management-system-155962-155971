import sqlite3
from typing import Iterable, Optional


def _configure_connection(conn: sqlite3.Connection) -> None:
    """Configure SQLite connection pragmas and row factory."""
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    # Performance pragmas for demo purposes; adjust if needed.
    conn.execute("PRAGMA journal_mode = WAL;")


# PUBLIC_INTERFACE
def open_connection(db_path: str) -> sqlite3.Connection:
    """Open a sqlite3 connection with sane defaults and return it."""
    # Using check_same_thread=False allows use across async contexts;
    # we still create/close per-request via dependencies.
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    _configure_connection(conn)
    return conn


# PUBLIC_INTERFACE
def init_db(db_path: str) -> None:
    """Initialize the SQLite database schema if it does not already exist."""
    conn = open_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def _execute_script(conn: sqlite3.Connection, sql: str, params: Optional[Iterable] = None) -> sqlite3.Cursor:
    """Helper for executing SQL with parameters."""
    cur = conn.cursor()
    cur.execute(sql, params or [])
    return cur

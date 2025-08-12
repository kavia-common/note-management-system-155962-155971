from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .models import NoteOut


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_note_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a sqlite Row to a dict suitable for NoteOut."""
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _fetch_one(conn: sqlite3.Connection, sql: str, params: Tuple[Any, ...]) -> Optional[Dict[str, Any]]:
    cur = conn.execute(sql, params)
    row = cur.fetchone()
    if not row:
        return None
    return _row_to_note_dict(row)


# PUBLIC_INTERFACE
def create_note(conn: sqlite3.Connection, title: str, content: Optional[str]) -> NoteOut:
    """Create a new note and return it."""
    now = _now_iso()
    cur = conn.execute(
        "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (title, content, now, now),
    )
    note_id = cur.lastrowid
    conn.commit()
    created = _fetch_one(conn, "SELECT * FROM notes WHERE id = ?", (note_id,))
    assert created is not None  # Newly inserted row must exist
    return NoteOut.model_validate(created)


# PUBLIC_INTERFACE
def get_note(conn: sqlite3.Connection, note_id: int) -> Optional[NoteOut]:
    """Fetch a single note by ID."""
    row_dict = _fetch_one(conn, "SELECT * FROM notes WHERE id = ?", (note_id,))
    return NoteOut.model_validate(row_dict) if row_dict else None


# PUBLIC_INTERFACE
def list_notes(conn: sqlite3.Connection, offset: int = 0, limit: int = 100) -> List[NoteOut]:
    """List notes ordered by updated_at descending, with pagination."""
    cur = conn.execute(
        "SELECT * FROM notes ORDER BY datetime(updated_at) DESC, id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    rows = cur.fetchall()
    return [NoteOut.model_validate(_row_to_note_dict(r)) for r in rows]


# PUBLIC_INTERFACE
def update_note(
    conn: sqlite3.Connection, note_id: int, title: Optional[str] = None, content: Optional[str] = None
) -> Optional[NoteOut]:
    """Update a note's title/content and return the updated note if it exists."""
    exists = _fetch_one(conn, "SELECT id FROM notes WHERE id = ?", (note_id,))
    if not exists:
        return None

    fields = []
    params: List[Any] = []

    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if content is not None:
        fields.append("content = ?")
        params.append(content)

    fields.append("updated_at = ?")
    params.append(_now_iso())

    params.append(note_id)

    sql = f"UPDATE notes SET {', '.join(fields)} WHERE id = ?"
    conn.execute(sql, tuple(params))
    conn.commit()

    updated = _fetch_one(conn, "SELECT * FROM notes WHERE id = ?", (note_id,))
    return NoteOut.model_validate(updated) if updated else None


# PUBLIC_INTERFACE
def delete_note(conn: sqlite3.Connection, note_id: int) -> bool:
    """Delete a note by ID. Returns True if the note existed and was deleted."""
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    return cur.rowcount > 0

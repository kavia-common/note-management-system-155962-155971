from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from ..config import get_settings, Settings
from ..db import open_connection
from ..models import NoteCreate, NoteOut, NoteUpdate
from ..repository import create_note, delete_note, get_note, list_notes, update_note

router = APIRouter(prefix="/notes", tags=["Notes"])


def _get_db_conn(settings: Settings = Depends(get_settings)):
    """Dependency to open and yield a DB connection per-request, ensuring clean close."""
    conn = open_connection(settings.notes_db_path)
    try:
        yield conn
    finally:
        conn.close()


# PUBLIC_INTERFACE
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=NoteOut,
    summary="Create a new note",
    description="Create a note with a title and optional content. Returns the created note.",
    responses={
        201: {"description": "Note created successfully"},
        400: {"description": "Bad Request: invalid input"},
    },
)
def create_note_endpoint(
    payload: NoteCreate,
    settings: Settings = Depends(get_settings),
    conn=Depends(_get_db_conn),
) -> NoteOut:
    """Create a note."""
    return create_note(conn, title=payload.title, content=payload.content)


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes",
    description="List notes with pagination, ordered by last update time (descending).",
)
def list_notes_endpoint(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return"),
    settings: Settings = Depends(get_settings),
    conn=Depends(_get_db_conn),
) -> List[NoteOut]:
    """List notes with pagination."""
    return list_notes(conn, offset=offset, limit=limit)


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Fetch a single note by its ID.",
    responses={404: {"description": "Note not found"}},
)
def get_note_endpoint(
    note_id: int = Path(..., ge=1, description="ID of the note to fetch"),
    settings: Settings = Depends(get_settings),
    conn=Depends(_get_db_conn),
) -> NoteOut:
    """Fetch a note by ID."""
    note = get_note(conn, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update a note's title and/or content. Returns the updated note.",
    responses={404: {"description": "Note not found"}},
)
def update_note_endpoint(
    payload: NoteUpdate,
    note_id: int = Path(..., ge=1, description="ID of the note to update"),
    settings: Settings = Depends(get_settings),
    conn=Depends(_get_db_conn),
) -> NoteOut:
    """Update a note by ID."""
    updated = update_note(conn, note_id=note_id, title=payload.title, content=payload.content)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note by its ID. Returns 204 No Content on success.",
    responses={404: {"description": "Note not found"}},
)
def delete_note_endpoint(
    note_id: int = Path(..., ge=1, description="ID of the note to delete"),
    settings: Settings = Depends(get_settings),
    conn=Depends(_get_db_conn),
) -> Response:
    """Delete a note by ID."""
    deleted = delete_note(conn, note_id=note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class NoteBase(BaseModel):
    """Base model with common fields (none required here)."""
    title: Optional[str] = Field(default=None, description="Title of the note")
    content: Optional[str] = Field(default=None, description="Content/body of the note")


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the note")
    content: Optional[str] = Field(default=None, description="Content/body of the note")


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="New title for the note")
    content: Optional[str] = Field(default=None, description="New content for the note")

    @model_validator(mode="after")
    def at_least_one_field(self) -> "NoteUpdate":
        """Ensure at least one field is provided for update."""
        if self.title is None and self.content is None:
            raise ValueError("At least one of 'title' or 'content' must be provided")
        return self


class NoteOut(BaseModel):
    id: int = Field(..., description="Unique identifier of the note")
    title: str = Field(..., description="Title of the note")
    content: Optional[str] = Field(default=None, description="Content/body of the note")
    created_at: datetime = Field(..., description="Creation timestamp in ISO 8601 format (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp in ISO 8601 format (UTC)")

    class Config:
        from_attributes = True  # Allow ORM-like conversion if used

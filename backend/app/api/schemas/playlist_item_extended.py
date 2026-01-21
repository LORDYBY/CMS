from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class MediaVersionOut(BaseModel):
    id: UUID
    number: int
    state: str
    created_at: datetime
    approved_at: datetime | None


class MediaOut(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    version: MediaVersionOut
    url: str


class PlaylistItemExtendedOut(BaseModel):
    id: UUID
    position: int
    duration_seconds: int | None
    media: MediaOut


class PlaylistExtendedOut(BaseModel):
    playlist_id: UUID
    items: list[PlaylistItemExtendedOut]

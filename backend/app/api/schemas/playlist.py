from pydantic import BaseModel, UUID4

class PlaylistItemCreate(BaseModel):
    content_version_id: UUID4
    duration_seconds: int | None = None
class CreatePlaylistRequest(BaseModel):
    name: str
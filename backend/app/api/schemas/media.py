from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime


class MediaVersionOut(BaseModel):
    version_number: int
    state: str
    created_at: datetime
    url: HttpUrl


class MediaAssetOut(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    created_at: datetime
    latest_version: MediaVersionOut


class MediaListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[MediaAssetOut]

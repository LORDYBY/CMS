from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Media:
    id: UUID
    filename: str
    mime_type: str
    checksum: str
    size_bytes: int
    created_at: datetime

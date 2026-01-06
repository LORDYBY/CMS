from pydantic import BaseModel
from uuid import UUID


class DeviceApproveRequest(BaseModel):
    tenant_id: UUID
    name: str | None = None
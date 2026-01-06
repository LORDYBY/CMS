from pydantic import BaseModel
from uuid import UUID

class DeviceRegisterRequest(BaseModel):
    fingerprint: str

class DeviceRegisterResponse(BaseModel):
    device_id: UUID
    state: str

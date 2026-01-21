from pydantic import BaseModel, EmailStr
from uuid import UUID


class LoginRequest(BaseModel):
    tenant_id: UUID
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RootLoginRequest(BaseModel):
    email: EmailStr
    password: str
from pathlib import Path
from app.settings import settings

def tenant_root(tenant_id: str) -> Path:
    return settings.MEDIA_ROOT / "tenants" / tenant_id

def tenant_media_root(tenant_id: str) -> Path:
    return tenant_root(tenant_id) / "media"

def tenant_emergency_root(tenant_id: str) -> Path:
    return tenant_root(tenant_id) / "emergency"
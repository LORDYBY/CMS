from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.common.device_commands import DeviceCommandEnum

class DeviceCommand(BaseModel):
    type: DeviceCommandEnum     # <--- use enum
    payload: Optional[Dict[str, Any]] = None

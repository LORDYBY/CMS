# app/common/device_commands.py

from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, Optional


class DeviceCommandEnum(str, Enum):
    reload_playlist = "reload_playlist"
    play = "play"
    pause = "pause"
    stop = "stop"
    emergency_show = "emergency_show"
    emergency_hide = "emergency_hide"
    ping = "ping"
    reboot = "reboot"
    shutdown = "shutdown"


class DeviceCommand(BaseModel):
    type: DeviceCommandEnum
    payload: Optional[Dict[str, Any]] = None

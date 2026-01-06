from fastapi import APIRouter
from app.api.ws.device import device_ws
from app.api.ws.admin import admin_ws

router = APIRouter(prefix="/ws")

router.add_api_websocket_route("/device", device_ws)
router.add_api_websocket_route("/admin", admin_ws)

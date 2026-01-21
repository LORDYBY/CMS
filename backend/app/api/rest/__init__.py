from fastapi import APIRouter

from app.api.rest.health import router as health_router
from app.api.rest.auth import router as auth_router
from app.api.rest.devices import router as devices_router
#from app.api.rest.device_admin import router as device_admin_router
from app.api.ws.router import router as ws_router
from app.api.rest.media import router as media_router
from app.api.rest.playlists import router as playlists_router

router = APIRouter()

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(devices_router)
#router.include_router(device_admin_router)
router.include_router(ws_router)
router.include_router(media_router)
router.include_router(playlists_router)


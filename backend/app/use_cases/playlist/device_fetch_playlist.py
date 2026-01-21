
#########################################
# import uuid
# from fastapi import Request
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from app.settings import settings
# from app.infrastructure.db.models.device import Device
# from app.infrastructure.db.models.device_playlist_assignment import DevicePlaylistAssignment
# from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository
# from app.common.http import get_public_base_url

# class DeviceFetchPlaylistUseCase:

#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self.playlist_repo = PlaylistRepository(session)

#     async def execute(self, device_id: uuid.UUID, request: Request):

#         # 1. Make sure device exists
#         stmt_device = select(Device).where(Device.id == device_id)
#         res = await self.session.execute(stmt_device)
#         device = res.scalar_one_or_none()
#         if not device:
#             raise ValueError("Device not found")

#         # 2. Get latest playlist assignment
#         stmt_assignment = (
#             select(DevicePlaylistAssignment)
#             .where(DevicePlaylistAssignment.device_id == device_id)
#             .order_by(DevicePlaylistAssignment.assigned_at.desc())
#             .limit(1)
#         )
#         res2 = await self.session.execute(stmt_assignment)
#         assignment = res2.scalar_one_or_none()
#         if not assignment:
#             raise ValueError("No playlist assigned to this device")

#         playlist_id = assignment.playlist_id

#         # 3. Fetch playlist items
#         rows = await self.playlist_repo.list_items_with_media(playlist_id)

#         items = []
#         base_url = settings.MEDIA_PUBLIC_BASE_URL.rstrip("/")

#         for item, version, asset in rows:

#             # Detect media type
#             is_video = asset.mime_type.startswith("video/")
#             duration = None if is_video else item.duration_seconds

#             # Build absolute media URL
#             media_url = (
#                 f"{base_url}/media/tenants/{asset.tenant_id}/media/"
#                 f"{asset.id}/v{version.version_number}/{asset.filename}"
#             )

#             items.append({
#                 "item_id": str(item.id),
#                 "position": item.position,
#                 "duration_seconds": duration,
#                 "media": {
#                     "media_id": str(asset.id),
#                     "filename": asset.filename,
#                     "mime_type": asset.mime_type,
#                     "url": media_url
#                 }
#             })

#         return {
#             "playlist_id": str(playlist_id),
#             "items": items
#         }
#########################################

import uuid
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.models.device import Device
from app.infrastructure.db.models.device_playlist_assignment import DevicePlaylistAssignment
from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository
from app.common.http import get_public_base_url


class DeviceFetchPlaylistUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.playlist_repo = PlaylistRepository(session)

    async def execute(self, device_id: uuid.UUID, request: Request):

        # ---------------------------------------------------------
        # 1. Ensure device exists
        # ---------------------------------------------------------
        res = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        device = res.scalar_one_or_none()

        # if not device:
        #     raise ValueError("Device not found")
        if not device:
            return {
                "items": [],
                "state": "REVOKED or NOT FOUND"
            }

        # ---------------------------------------------------------
        # 2. Get latest playlist assignment
        # ---------------------------------------------------------
        res = await self.session.execute(
            select(DevicePlaylistAssignment)
            .where(DevicePlaylistAssignment.device_id == device_id)
            .order_by(DevicePlaylistAssignment.assigned_at.desc())
            .limit(1)
        )
        assignment = res.scalar_one_or_none()

        # if not assignment:
        #     raise ValueError("No playlist assigned to this device")
        if not assignment:
            return {
                "playlist_id": None,
                "items": []
            }
        playlist_id = assignment.playlist_id

        # ---------------------------------------------------------
        # 3. Fetch playlist items
        # ---------------------------------------------------------
        rows = await self.playlist_repo.list_items_with_media(playlist_id)

        # ✅ IMPORTANT: resolve public base URL dynamically
        base_url = get_public_base_url(request).rstrip("/")

        items = []

        for item, version, asset in rows:
            is_video = asset.mime_type.startswith("video/")
            duration = None if is_video else item.duration_seconds

            media_url = (
                f"{base_url}/media/tenants/{asset.tenant_id}/media/"
                f"{asset.id}/v{version.version_number}/{asset.filename}"
            )

            items.append({
                "item_id": str(item.id),
                "position": item.position,
                "duration_seconds": duration,
                "media": {
                    "media_id": str(asset.id),
                    "filename": asset.filename,
                    "mime_type": asset.mime_type,
                    "url": media_url,
                }
            })

        # ---------------------------------------------------------
        # 4. Response
        # ---------------------------------------------------------
        return {
            "playlist_id": str(playlist_id),
            "items": items,
        }


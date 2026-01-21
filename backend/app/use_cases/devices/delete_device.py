# app/use_cases/devices/delete_device.py

from sqlalchemy import delete, select
from app.infrastructure.db.models.device import Device
from app.infrastructure.db.models.device_playlist_assignment import DevicePlaylistAssignment


class DeleteDeviceUseCase:

    def __init__(self, session):
        self.session = session

    async def execute(self, device_id):

        # 1️⃣ Remove playlist assignments
        await self.session.execute(
            delete(DevicePlaylistAssignment)
            .where(DevicePlaylistAssignment.device_id == device_id)
        )

        # 2️⃣ Delete device
        device = await self.session.get(Device, device_id)

        if not device:
            return

        await self.session.delete(device)

        # 3️⃣ Commit once
        await self.session.commit()
# app/use_cases/devices/remove_device_playlist.py
from sqlalchemy import delete
from app.infrastructure.db.models.device_playlist_assignment import DevicePlaylistAssignment


class RemoveDevicePlaylistUseCase:

    def __init__(self, session):
        self.session = session

    async def execute(self, device_id):
        await self.session.execute(
            delete(DevicePlaylistAssignment)
            .where(DevicePlaylistAssignment.device_id == device_id)
        )

        await self.session.commit()

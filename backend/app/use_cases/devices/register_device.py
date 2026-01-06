from app.infrastructure.db.models.device import Device
from app.infrastructure.db.repositories.device_repository import DeviceRepository
from app.use_cases.audit.write_audit_log import write_audit

class RegisterDeviceUseCase:

    def __init__(self, session):
        self.repo = DeviceRepository(session)
        self.session = session

    async def execute(self, fingerprint: str):
        existing = await self.repo.get_by_fingerprint(fingerprint)
        if existing:
            return existing

        device = Device(fingerprint=fingerprint)
        await self.repo.save(device)

        await write_audit(
            self.session,
            actor="DEVICE",
            action="REGISTER",
            entity="device",
            entity_id=device.id
        )

        return device

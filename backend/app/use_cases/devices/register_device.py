# from app.infrastructure.db.models.device import Device
# from app.infrastructure.db.repositories.device_repository import DeviceRepository
# from app.use_cases.audit.write_audit_log import write_audit

# class RegisterDeviceUseCase:

#     def __init__(self, session):
#         self.repo = DeviceRepository(session)
#         self.session = session

#     async def execute(self, fingerprint: str):
#         existing = await self.repo.get_by_fingerprint(fingerprint)
#         if existing:
#             return existing

#         device = Device(fingerprint=fingerprint)
#         await self.repo.save(device)

#         await write_audit(
#             self.session,
#             actor="DEVICE",
#             action="REGISTER",
#             entity="device",
#             entity_id=device.id
#         )

#         return device

# app/use_cases/devices/register_device.py
from sqlalchemy import select
from app.infrastructure.db.models.device import Device
from app.common.device_tokens import generate_device_token, hash_device_token
from app.common.time import time
from app.api.schemas.device import DeviceRegisterResponse


class RegisterDeviceUseCase:

    def __init__(self, session):
        self.session = session

    async def execute(self, fingerprint: str) -> DeviceRegisterResponse:

        result = await self.session.execute(
            select(Device).where(Device.fingerprint == fingerprint)
        )
        device = result.scalar_one_or_none()

        # ----------------------------------------------------
        # EXISTING DEVICE
        # ----------------------------------------------------
        if device:

            # 🔒 revoked or blocked
            if device.revoked_at is not None or device.state == "BLOCKED":
                return DeviceRegisterResponse(
                    device_id=device.id,
                    state="REVOKED",
                    token=None
                )

            # ✅ approved → rotate token
            if device.state == "APPROVED":
                raw_token = generate_device_token()
                device.token_hash = hash_device_token(raw_token)
                device.approved_at = time.local_now()

                await self.session.commit()

                return DeviceRegisterResponse(
                    device_id=device.id,
                    state="APPROVED",
                    token=raw_token
                )

            # ⏳ pending
            return DeviceRegisterResponse(
                device_id=device.id,
                state="PENDING",
                token=None
            )

        # ----------------------------------------------------
        # NEW DEVICE
        # ----------------------------------------------------
        device = Device(
            fingerprint=fingerprint,
            state="PENDING"
        )

        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)

        return DeviceRegisterResponse(
            device_id=device.id,
            state="PENDING",
            token=None
        )

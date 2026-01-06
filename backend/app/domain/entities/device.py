from app.domain.enums.device_state import DeviceState

class DeviceDomain:
    def __init__(self, model):
        self.model = model

    def approve(self):
        if self.model.state != DeviceState.PENDING:
            raise ValueError("Invalid device state")
        self.model.state = DeviceState.APPROVED

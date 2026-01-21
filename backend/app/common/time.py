from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os

load_dotenv()

class time:
    @staticmethod
    def tz():
        # Always read environment directly
        tz_name = os.environ.get("APP_TIMEZONE", "UTC")
        try:
            return ZoneInfo(tz_name)
        except Exception:
            return timezone.utc

    @staticmethod
    def utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def local_now() -> datetime:
        return datetime.now(time.tz())

    @staticmethod
    def date_str() -> str:
        now = time.local_now()
        return now.strftime("%d/%m/%Y")

    @staticmethod
    def time_str() -> str:
        now = time.local_now()
        ms = int(now.microsecond / 1000)
        return now.strftime(f"%H:%M:%S:{ms:03d}")

    @staticmethod
    def datetime_str() -> str:
        now = time.local_now()
        ms = int(now.microsecond / 1000)
        return now.strftime(f"%d/%m/%Y %H:%M:%S:{ms:03d}")

from pathlib import Path
from app.settings import settings


def media_asset_dir(tenant_id, media_id) -> Path:
    return (
        settings.MEDIA_ROOT
        / "tenants"
        / str(tenant_id)
        / "media"
        / str(media_id)
    )


def media_version_path(tenant_id, media_id, version, filename) -> Path:
    base = media_asset_dir(tenant_id, media_id)
    return base / f"v{version}" / filename


class FileStorage:

    def save_version(self, tenant_id, media_id, version_number, filename, data: bytes):
        version_dir = (
            settings.MEDIA_ROOT #### this line changed
            / "tenants"
            / str(tenant_id)
            / "media"
            / str(media_id)
            / f"v{version_number}"
        )

        version_dir.mkdir(parents=True, exist_ok=True)

        file_path = version_dir / filename
        file_path.write_bytes(data)
        return file_path

from app.infrastructure.db.repositories.media_repository import MediaRepository
from app.api.schemas.media import MediaAssetOut, MediaVersionOut, MediaListResponse

class ListMediaUseCase:

    def __init__(self, repository: MediaRepository):
        self.repository = repository

    async def execute(self, session, tenant_id, limit, offset, search):
        total, rows = await self.repository.list_media(
            session, tenant_id, limit, offset, search
        )

        items = []
        for asset, version in rows:
            public_url = (
                f"http://localhost:8080/media/tenants/{tenant_id}/media/"
                f"{asset.id}/v{version.version_number}/{asset.filename}"
            )

            items.append(
                MediaAssetOut(
                    id=asset.id,
                    tenant_id=asset.tenant_id,
                    filename=asset.filename,
                    mime_type=asset.mime_type,
                    size_bytes=asset.size_bytes,
                    checksum=asset.checksum,
                    created_at=asset.created_at,
                    latest_version=MediaVersionOut(
                        version_number=version.version_number,
                        state=version.state.value,
                        created_at=version.created_at,
                        url=public_url,
                    ),
                )
            )

        return MediaListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )
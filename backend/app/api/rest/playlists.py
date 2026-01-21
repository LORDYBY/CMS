# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import BaseModel

# from app.dependencies import get_current_user
# from app.infrastructure.db.session import get_db
# from app.use_cases.playlist.create_playlist import CreatePlaylistUseCase

# router = APIRouter(prefix="/playlists", tags=["Playlists"])


# class CreatePlaylistRequest(BaseModel):
#     name: str


# @router.post("")
# async def create_playlist(
#     data: CreatePlaylistRequest,
#     user=Depends(get_current_user),
#     session: AsyncSession = Depends(get_db)
# ):
#     use_case = CreatePlaylistUseCase(session)
#     result = await use_case.execute(
#         tenant_id=user.tenant_id,
#         name=data.name,
#         created_by=user.id,
#     )
#     return result

import uuid
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.infrastructure.db.session import get_db
from app.use_cases.playlist.add_playlist_item import AddPlaylistItemUseCase
from app.api.schemas.playlist import PlaylistItemCreate
from app.infrastructure.db.repositories.playlist_repository import PlaylistRepository
from app.api.schemas.playlist_item_extended import PlaylistExtendedOut, PlaylistItemExtendedOut, MediaOut, MediaVersionOut
from app.use_cases.playlist.publish_playlist import PublishPlaylistUseCase
from app.use_cases.playlist.create_playlist import CreatePlaylistUseCase
from app.api.schemas.playlist import CreatePlaylistRequest

from app.settings import settings


router = APIRouter(prefix="/playlists", tags=["Playlists"])

@router.post("")
# async def create_playlist(
#     payload: CreatePlaylistRequest,
#     user=Depends(get_current_user),
#     session: AsyncSession = Depends(get_db)
# ):
#     use_case = CreatePlaylistUseCase(session)
#     result = await use_case.execute(tenant_id=user.tenant_id, name=payload.name)
#     return result
async def create_playlist(
    payload: CreatePlaylistRequest,
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    use_case = CreatePlaylistUseCase(session)

    return await use_case.execute(
        tenant_id=user.tenant_id,
        name=payload.name,
        created_by=user.id,
    )

@router.post("/{playlist_id}/items")
async def add_item_to_playlist(
    #playlist_id: str,
    playlist_id: UUID,
    body: PlaylistItemCreate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    use_case = AddPlaylistItemUseCase(session)
    result = await use_case.execute(
        tenant_id=user.tenant_id,
        playlist_id=playlist_id,
        content_version_id=body.content_version_id,
        duration_seconds=body.duration_seconds,
    )
    return result


@router.get("/{playlist_id}/items", response_model=PlaylistExtendedOut)
async def list_playlist_items(
    playlist_id: uuid.UUID,
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    repo = PlaylistRepository(session)
    rows = await repo.list_items_with_media(playlist_id)

    items = []

    for (item, version, asset) in rows:
        public_url = (
            f"{settings.MEDIA_PUBLIC_BASE_URL}/media/tenants/"
            f"{asset.tenant_id}/media/{asset.id}/v{version.version_number}/{asset.filename}"
        )

        items.append(
            PlaylistItemExtendedOut(
                id=item.id,
                position=item.position,
                duration_seconds=item.duration_seconds,
                media=MediaOut(
                    id=asset.id,
                    filename=asset.filename,
                    mime_type=asset.mime_type,
                    size_bytes=asset.size_bytes,
                    checksum=asset.checksum,
                    url=public_url,
                    version=MediaVersionOut(
                        id=version.id,
                        number=version.version_number,
                        state=version.state.value,
                        created_at=version.created_at,
                        approved_at=version.approved_at,
                    ),
                ),
            )
        )

    return PlaylistExtendedOut(
        playlist_id=playlist_id,
        items=items,
    )
@router.post("/{playlist_id}/publish")
async def publish_playlist(
    playlist_id: UUID,
    session: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),   
):
    use_case = PublishPlaylistUseCase(session)
    result = await use_case.execute(playlist_id, user.tenant_id)
    return result
from pathlib import Path
from fastapi import Query, APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.dependencies import get_current_user
from app.infrastructure.db.session import get_db

# USE CASES
from app.use_cases.content.upload_media import UploadMediaUseCase
from app.use_cases.content.upload_new_version import UploadNewVersionUseCase
from app.use_cases.content.list_media import ListMediaUseCase
from app.use_cases.content.approve_version import ApproveVersionUseCase

# REPOSITORY + STORAGE
from app.infrastructure.db.repositories.media_repository import MediaRepository
from app.infrastructure.filesystem.media_storage import FileStorage

# SCHEMAS
from app.api.schemas.media import MediaListResponse


router = APIRouter(prefix="/media", tags=["Media"])


# ---------------------------------------------------------
# 1) UPLOAD NEW MEDIA (creates v1)
# ---------------------------------------------------------
@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    use_case = UploadMediaUseCase(
        repository=MediaRepository(session),
        file_storage=FileStorage()
    )

    return await use_case.execute(
        #session=session,
        tenant_id=user.tenant_id,
        created_by=user.id,
        file=file,
    )


# ---------------------------------------------------------
# 2) LIST MEDIA (with latest version + URL)
# ---------------------------------------------------------
@router.get("/", response_model=MediaListResponse)
async def list_media(
    user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    use_case = ListMediaUseCase(MediaRepository(session))

    return await use_case.execute(
        session=session,
        tenant_id=user.tenant_id,
        limit=limit,
        offset=offset,
        search=search,
    )


# ---------------------------------------------------------
# 3) UPLOAD NEW VERSION (v2, v3…)
# ---------------------------------------------------------
@router.post("/{media_id}/upload-version")
async def upload_new_version(
    media_id: uuid.UUID,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    use_case = UploadNewVersionUseCase(session)

    return await use_case.execute(
        media_id=media_id,
        file=file,
        user_id=user.id,
    )


# ---------------------------------------------------------
# 4) APPROVE A VERSION
# ---------------------------------------------------------
@router.post("/{media_id}/approve/{version_number}")
async def approve_version(
    media_id: uuid.UUID,
    version_number: int,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    use_case = ApproveVersionUseCase(session)

    return await use_case.execute(
        media_id=media_id,
        version_number=version_number,
        approver_id=user.id,
    )

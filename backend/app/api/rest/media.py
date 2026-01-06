import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db
from app.use_cases.content.upload_media import UploadMediaUseCase
from app.dependencies import get_current_user

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        temp_path = Path(tmp.name)

    use_case = UploadMediaUseCase(session)
    return await use_case.execute(
        temp_path=temp_path,
        filename=file.filename,
        mime_type=file.content_type,
    )

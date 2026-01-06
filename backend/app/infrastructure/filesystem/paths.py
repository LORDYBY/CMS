from pathlib import Path

MEDIA_ROOT = Path("/media")  # Docker mount
UPLOADS_DIR = MEDIA_ROOT / "uploads"
THUMBNAILS_DIR = MEDIA_ROOT / "thumbnails"

def ensure_directories() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile


class FileClerk:
    """
    FileClerk handles storing uploaded files from FastAPI in an organized directory structure.
    Files are stored in a path pattern: base_dir/year/month/uuid/original_filename
    """

    def __init__(self, base_dir: str = "storage"):
        self.base_dir = base_dir

    async def store(self, file: UploadFile) -> Tuple[str, str]:
        """
        Store a file in the organized storage system.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Tuple[str, str]: (full storage path, unique identifier)
        """
        path, file_uuid = self._generate_path(file.filename)
        self._ensure_storage_path(path)

        # Save the uploaded file
        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return str(path), file_uuid

    def _generate_path(self, original_filename: str) -> Tuple[Path, str]:
        """Generate storage path preserving original filename"""
        now = datetime.now()
        file_uuid = str(uuid.uuid4())

        path = Path(
            self.base_dir,
            now.strftime("%Y"),
            now.strftime("%m"),
            file_uuid,
            self._sanitize_filename(original_filename),
        )

        return path, file_uuid

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Clean filename to remove problematic characters"""
        import re

        return re.sub(r"[^\w\-\.]", "_", filename)

    @staticmethod
    def _ensure_storage_path(path: Path):
        """Create the directory structure if it doesn't exist"""
        path.parent.mkdir(parents=True, exist_ok=True)


# Example usage with FastAPI:
"""
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()
clerk = FileClerk()

@app.post("/upload/")
async def upload_file(file: UploadFile):
    stored_path, file_id = await clerk.store(file)
    return JSONResponse({
        "file_id": file_id,
        "path": stored_path,
        "filename": file.filename
    })
"""

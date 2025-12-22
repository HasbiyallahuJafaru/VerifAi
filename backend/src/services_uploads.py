import os
import uuid
from datetime import datetime
from typing import Tuple

from .errors import ValidationError
from .database import session_scope
from .models import Upload


def allowed_file(filename: str, allowed_extensions: list) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_upload(file_storage, upload_dir: str, allowed_extensions: list, max_file_size: int) -> dict:
    if not file_storage or file_storage.filename == "":
        raise ValidationError("No file selected")

    if not allowed_file(file_storage.filename, allowed_extensions):
        raise ValidationError("File type not allowed")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > max_file_size:
        raise ValidationError("File too large")

    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file_storage.filename
    stored_name = f"{timestamp}_{original_filename}"
    filepath = os.path.join(upload_dir, stored_name)
    file_storage.save(filepath)

    record = Upload(
        id=str(uuid.uuid4()),
        filename=stored_name,
        original_filename=original_filename,
        filepath=filepath,
        file_size=size,
        document_type="unknown",
        verification_id=None,
    )

    with session_scope() as db:
        db.add(record)

    return {
        "upload_id": record.id,
        "filename": stored_name,
        "file_size": size,
        "uploaded_at": datetime.now().isoformat(),
    }

from pydantic import BaseModel
from uuid import UUID


class UploadFileResponse(BaseModel):
    file_id: UUID

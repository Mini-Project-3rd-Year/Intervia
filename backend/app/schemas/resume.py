from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    raw_text: str | None
    created_at: datetime
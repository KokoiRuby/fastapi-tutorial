from pydantic import BaseModel, Field
from datetime import datetime, UTC


class User(BaseModel):
    user_id: int
    email: str | None = None
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))

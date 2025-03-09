from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.domain.models.base import BaseModel
import re

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


# kw_only=True means that all fields in the dataclass
# must be passed as keyword arguments when creating an instance.
@dataclass(kw_only=True)
class User(BaseModel):
    user_id: int
    email: str
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    update: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def validate_email(email: str) -> str:
        if not EMAIL_REGEX.match(email):
            raise ValueError("Invalid email")
        return email

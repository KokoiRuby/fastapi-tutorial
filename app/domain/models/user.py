from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.domain.models.base import BaseModel
import re
from app.domain.exceptions import InvalidFieldValue

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


# kw_only=True means that all fields in the dataclass
# must be passed as keyword arguments when creating an instance.
@dataclass(kw_only=True)
class User(BaseModel):
    user_id: int
    email: str | None = None
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def validate_email(email: str | None) -> str | None:
        if email is not None and not EMAIL_REGEX.match(email):
            # raise ValueError("Invalid email")
            raise InvalidFieldValue(field_name="email", field_value=email)
        return email

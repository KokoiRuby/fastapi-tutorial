from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.domain.models.base import BaseModel
from app.domain.models.user import User
from app.domain.exceptions import InvalidFieldValue


# kw_only=True means that all fields in the dataclass
# must be passed as keyword arguments when creating an instance.
@dataclass(kw_only=True)
class Post(BaseModel):
    post_id: int | None = None
    title: str
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = field(default_factory=lambda: datetime.now(UTC))
    user: User | None = field(default=None)

    @staticmethod
    def validate_title(title: str) -> str:
        if len(title.strip()) == 0:
            # raise ValueError("Title cannot be empty")
            raise InvalidFieldValue(field_name="title", field_value=title)
        return title.strip()


# post = Post(post_id=1, title="origin title")

# # validation required, raise Exception
# # post.title = ""

# # aware of modified fields
# post.title = "new title"
# assert post.modified_fields == {
#     "title": {
#         "original_value": "origin title",
#         "new_value": "new title"
#     }
# }

# # support rollback
# post.rollback()
# assert post.modified_fields == {}
# assert post.title == "origin title"

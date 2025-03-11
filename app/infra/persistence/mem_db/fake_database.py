from dataclasses import dataclass, field
from datetime import datetime
import random

# expose
__all__ = ("fake_database", "FakeDatabase", )


# simulate database
@dataclass
class FakeDatabase:
    posts: dict = field(default_factory=dict)  # each filed is a table
    users: dict = field(default_factory=dict)

    # called after __init__ to populate the tables
    def __post_init__(self):
        self.users = {
            # dict comprehension
            user_id: {
                "user_id": user_id,
                "email": f"user_{user_id}@example.com",
                "created": datetime.utcnow(),
                "updated": datetime.utcnow(),
            }
            for user_id in range(1, 6)
        }
        self.posts = {
            post_id: {
                "post_id": post_id,
                "title": f"FastAPI tutorial {post_id}",
                "created": datetime.utcnow(),
                "updated": datetime.utcnow(),
                "user_id": random.choice(list(self.users.keys())),
            }
            for post_id in range(1, 6)
        }


fake_database = FakeDatabase()

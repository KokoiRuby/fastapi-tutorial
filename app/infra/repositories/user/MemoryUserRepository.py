from app.infra.persistence.mem_db.fake_database import FakeDatabase
from app.domain.repositories import UserRepository
from app.domain.models.user import User


# subclassing UserRepository
class MemoryUserRepository(UserRepository):
    def __init__(self, database: FakeDatabase):
        self.database = database

    async def get_by_id(self, user_id: int) -> User | None:
        # get user from db
        if not (user_data := self.database.users.get(user_id)):
            return None

        # deserialize user (to domain model)
        return self._to_user_model(user_data)

    def _to_user_model(self, user_data: dict) -> User:
        return User(**user_data)

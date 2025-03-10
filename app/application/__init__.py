from app.application.dic import DIC
from app.infra.repositories import MemoryUserRepository, MeoryPostRepository
from app.infra.persistence.mem_db.fake_database import fake_database
from app.application.post_service import PostService


async def application_startup():
    user_repository = MemoryUserRepository(database=fake_database)
    post_repository = MeoryPostRepository(database=fake_database)

    DIC.post_service = PostService(
        post_repository=post_repository,
        user_repository=user_repository,
    )

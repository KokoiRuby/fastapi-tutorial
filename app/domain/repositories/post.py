from abc import ABC, abstractmethod
from app.domain.models.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post: ...

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Post | None: ...

    @abstractmethod
    async def get_posts(self) -> list[Post]: ...

    @abstractmethod
    async def update(self, post: Post) -> Post: ...

    @abstractmethod
    async def delete(self, post_id: int) -> None: ...

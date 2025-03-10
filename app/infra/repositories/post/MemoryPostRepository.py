from app.infra.persistence.mem_db.fake_database import FakeDatabase
from app.domain.repositories import PostRepository
from app.domain.models.post import Post
from app.domain.models.user import User


# subclassing PostRepository
class MeoryPostRepository(PostRepository):
    def __init__(self, database: FakeDatabase) -> None:
        self.database = database

    async def create(self, post: Post) -> Post:
        # serialize (from domain model to dict)
        post_data = self._serialize(post)
        # persist
        self.database.posts[post_data["post_id"]] = post_data
        # update id and return
        post.post_id = post_data["post_id"]
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        if not (post_data := self.database.posts.get(post_id)):
            return None

        # deserialize (from dict to domain model) and return
        return self._build_post_model(post_data)

    async def get_posts(self) -> list[Post]:
        # iter + deserialize (from dict to domain model) and return
        return [self._build_post_model(post_data) for post_data in self.database.posts.values()]

    async def update(self, post: Post) -> Post:
        # return if nothing to update
        if not post.modified_fields:
            return post
        # otherwise partial update
        self.database.posts[post.post_id].update(
            self._serialize(post, partial=True))
        return post

    async def delete(self, post_id: int) -> None:
        try:
            self.database.posts.pop(post_id)
        except KeyError:
            return None

    def _serialize(self, post: Post, partial: bool = False) -> dict:
        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if not partial:
            return {
                "post_id": post.post_id or self._generate_id(),
                "title": post.title,
                "created": post.created,
                "updated": post.updated,
                "user_id": post.user.user_id,
            }
        else:
            data = {}
            modified_fields = post.modified_fields
            for field in modified_fields:
                match field:
                    case "title":
                        data["title"] = post.title
                    case _:
                        ...

            return data

    def _generate_id(self) -> int:
        return len(self.database.posts) + 1

    def _build_post_model(self, post_data: dict) -> Post:
        return Post(
            post_id=post_data["post_id"],
            title=post_data["title"],
            created=post_data["created"],
            updated=post_data["updated"],
            user=User(
                user_id=post_data["user_id"],
            )
        )

from app.infra.persistence.mysql.database import Database
from app.domain.repositories import PostRepository
from app.domain.models.post import Post
from app.domain.models.user import User


# subclassing PostRepository
class MySQLPostRepository(PostRepository):
    def __init__(self, database: Database) -> None:
        self.connection_pool = database.pool  # get pool from database

    async def create(self, post: Post) -> Post:
        assert self.connection_pool
        async with self.connection_pool.acquire() as conn:  # get connection from pool
            async with conn.cursor() as cur:
                await cur.execute(
                    query="INSERT INTO posts (post_id, title, created, updated, user_id) VALUES (%s, %s, %s, %s, %s)",
                    args=(
                        post.post_id,
                        post.title,
                        post.created,
                        post.updated,
                        post.user.user_id,
                    ),
                )
                post.post_id = cur.lastrowid
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        assert self.connection_pool
        async with self.connection_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    query="SELECT post_id, title, created, updated, user_id FROM posts WHERE post_id = %s",
                    args=(post_id,),
                )
                post_data = await cur.fetchone()

        # deserialize (from dict to domain model) and return
        return self._build_post_model(post_data) if post_data else None

    async def get_posts(self) -> list[Post]:
        assert self.connection_pool
        async with self.connection_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    query="SELECT post_id, title, created, updated, user_id FROM posts"
                )
                posts = await cur.fetchall()

        # iter + deserialize (from dict to domain model) and return
        return [self._build_post_model(post_data) for post_data in posts]

    async def update(self, post: Post) -> Post:
        # return a empty dict if no fields are updated
        if not (modified_data := self._serialize(post=post, partial=True)):
            return post

        assert self.connection_pool
        async with self.connection_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    query=f"UPDATE posts SET {', '.join([f'`{key}` = %s' for key in modified_data.keys(
                    )])} WHERE post_id = %s",
                    args=tuple(modified_data.values()) + (post.post_id,),
                )

        return post

    async def delete(self, post_id: int) -> None:
        assert self.connection_pool
        async with self.connection_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    query="DELETE FROM posts WHERE post_id = %s",
                    args=(post_id,),
                )
            return None

    @staticmethod
    def _serialize(post: Post, partial: bool = False) -> dict:
        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if not partial:
            return {
                "post_id": post.post_id,
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

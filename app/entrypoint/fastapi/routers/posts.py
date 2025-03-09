from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.infra.persistence.mem_db.fake_database import fake_database
from app.entrypoint.fastapi.schema.post import Post, PostCreateInput, PostUpdateInput
from app.entrypoint.fastapi.schema.user import User
from starlette.exceptions import HTTPException

# expose
__all__ = ("router", )

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get(
    "",
    description="Get all posts",
    response_model=list[Post],
    status_code=status.HTTP_200_OK,
)
async def list_posts() -> list[Post]:
    return [
        Post(
            post_id=post["post_id"],
            title=post["title"],
            created=post["created"],
            user=User(
                user_id=post["user_id"],
                # get user by user_id in post
                email=fake_database.users[post["user_id"]]["email"],
                created=fake_database.users[post["user_id"]]["created"]
            )
        )
        for post in fake_database.posts.values()
    ]


@router.get(
    "/{post_id}",
    description="Get a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def get_post(post_id: int) -> Post:
    if post_id not in fake_database.posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post = fake_database.posts[post_id]

    return Post(
        post_id=post["post_id"],
        title=post["title"],
        created=post["created"],
        user=User(
            user_id=post["user_id"],
            email=fake_database.users[post["user_id"]]["email"],
            created=fake_database.users[post["user_id"]]["created"]
        )
    )


@router.post(
    "",
    description="Create a post",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(input_post: PostCreateInput) -> Post:
    if input_post.user_id not in fake_database.users:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # create post based on input
    post = Post(
        # increment
        post_id=len(fake_database.posts) + 1,
        title=input_post.title,
        user=User(
            user_id=input_post.user_id,
            email=fake_database.users[input_post.user_id]["email"],
            created=fake_database.users[input_post.user_id]["created"]
        ),
    )

    # add post to database
    fake_database.posts[post.post_id] = {
        "post_id": post.post_id,
        "title": post.title,
        "created": post.created,
        "user_id": post.user.user_id,
    }

    return post


@router.patch(
    "/{post_id}",
    description="Update a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def update_post(post_id: int, update_post: PostUpdateInput) -> Post:
    if post_id not in fake_database.posts:
        raise HTTPException(
            detail="Post not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update in db
    post = fake_database.posts[post_id]
    post["title"] = update_post.title

    # you cannot return `post` as it's dict
    return Post(
        post_id=post["post_id"],
        title=post["title"],
        created=post["created"],
        user=User(
            user_id=post["user_id"],
            email=fake_database.users[post["user_id"]]["email"],
            created=fake_database.users[post["user_id"]]["created"]
        )
    )


@router.delete(
    "/{post_id}",
    description="Delete a post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int) -> None:
    if post_id not in fake_database.posts:
        raise HTTPException(
            detail="Post not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # delete in db
    del fake_database.posts[post_id]
    return None

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
# from app.infra.persistence.mem_db.fake_database import fake_database
from app.entrypoint.fastapi.schema.post import Post, PostCreateInput, PostUpdateInput
from app.entrypoint.fastapi.schema.user import User
from starlette.exceptions import HTTPException
from app.application.dic import DIC
from app.domain.models.post import Post as PostModel
from app.domain.models.user import User as UserModel
from app.domain.exceptions import UserNotFound, PostNotFound, InvalidFieldValue, Forbiden

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
    assert DIC.post_service
    posts: list[PostModel] = await DIC.post_service.list_posts()
    return [to_post_view_model(post) for post in posts]


@router.get(
    "/{post_id}",
    description="Get a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def get_post(post_id: int) -> Post:
    assert DIC.post_service
    post: PostModel = await DIC.post_service.get_post(post_id)
    return to_post_view_model(post)


@router.post(
    "",
    description="Create a post",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(input_post: PostCreateInput) -> Post:
    assert DIC.post_service
    post: PostModel = await DIC.post_service.create_post(
        user_id=input_post.user_id,
        title=input_post.title
    )
    return to_post_view_model(post)


@router.patch(
    "/{post_id}",
    description="Update a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def update_post(post_id: int, update_post: PostUpdateInput) -> Post:
    assert DIC.post_service
    post: PostModel = await DIC.post_service.update_post(
        post_id=post_id,
        title=update_post.title,
        user_id=update_post.user_id
    )
    return to_post_view_model(post)


@router.delete(
    "/{post_id}",
    description="Delete a post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int) -> None:
    assert DIC.post_service
    await DIC.post_service.delete_post(post_id)


def to_post_view_model(post: PostModel) -> Post:
    assert post.user
    return Post(
        post_id=post.post_id,
        title=post.title,
        created=post.created,
        user=to_user_view_model(post.user)
    )


def to_user_view_model(user: UserModel) -> User:
    return User(
        user_id=user.user_id,
        email=user.email,
        created=user.created
    )

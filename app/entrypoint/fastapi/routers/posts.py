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
    # return [
    #     Post(
    #         post_id=post["post_id"],
    #         title=post["title"],
    #         created=post["created"],
    #         user=User(
    #             user_id=post["user_id"],
    #             # get user by user_id in post
    #             email=fake_database.users[post["user_id"]]["email"],
    #             created=fake_database.users[post["user_id"]]["created"]
    #         )
    #     )
    #     for post in fake_database.posts.values()
    # ]
    # get post service

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
    # if post_id not in fake_database.posts:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Post not found"
    #     )

    # post = fake_database.posts[post_id]

    # return Post(
    #     post_id=post["post_id"],
    #     title=post["title"],
    #     created=post["created"],
    #     user=User(
    #         user_id=post["user_id"],
    #         email=fake_database.users[post["user_id"]]["email"],
    #         created=fake_database.users[post["user_id"]]["created"]
    #     )
    # )
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.get_post(post_id)
        return to_post_view_model(post)
    except (PostNotFound, UserNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.post(
    "",
    description="Create a post",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(input_post: PostCreateInput) -> Post:
    # if input_post.user_id not in fake_database.users:
    #     raise HTTPException(
    #         detail="User not found",
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     )

    # # create post based on input
    # post = Post(
    #     # increment
    #     post_id=len(fake_database.posts) + 1,
    #     title=input_post.title,
    #     user=User(
    #         user_id=input_post.user_id,
    #         email=fake_database.users[input_post.user_id]["email"],
    #         created=fake_database.users[input_post.user_id]["created"]
    #     ),
    # )

    # # add post to database
    # fake_database.posts[post.post_id] = {
    #     "post_id": post.post_id,
    #     "title": post.title,
    #     "created": post.created,
    #     "user_id": post.user.user_id,
    # }

    # return post
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.create_post(
            user_id=input_post.user_id,
            title=input_post.title
        )
        return to_post_view_model(post)
    except (UserNotFound, InvalidFieldValue) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.patch(
    "/{post_id}",
    description="Update a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def update_post(post_id: int, update_post: PostUpdateInput) -> Post:
    # if post_id not in fake_database.posts:
    #     raise HTTPException(
    #         detail="Post not found",
    #         status_code=status.HTTP_404_NOT_FOUND,
    #     )

    # # update in db
    # post = fake_database.posts[post_id]
    # post["title"] = update_post.title

    # # you cannot return `post` as it's dict
    # return Post(
    #     post_id=post["post_id"],
    #     title=post["title"],
    #     created=post["created"],
    #     user=User(
    #         user_id=post["user_id"],
    #         email=fake_database.users[post["user_id"]]["email"],
    #         created=fake_database.users[post["user_id"]]["created"]
    #     )
    # )
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.update_post(
            post_id=post_id,
            title=update_post.title,
            user_id=update_post.user_id
        )
        return to_post_view_model(post)
    except Forbiden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except (PostNotFound, UserNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.delete(
    "/{post_id}",
    description="Delete a post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int) -> None:
    # if post_id not in fake_database.posts:
    #     raise HTTPException(
    #         detail="Post not found",
    #         status_code=status.HTTP_404_NOT_FOUND,
    #     )

    # # delete in db
    # del fake_database.posts[post_id]
    # return None
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

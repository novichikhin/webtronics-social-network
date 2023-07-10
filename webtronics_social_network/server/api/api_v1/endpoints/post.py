import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from webtronics_social_network import types, exceptions
from webtronics_social_network.database.redis.holder import RedisHolder
from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import PostgresHolderMarker
from webtronics_social_network.server.api.api_v1.dependencies.database.redis import RedisHolderMarker
from webtronics_social_network.server.api.api_v1.responses.user import user_auth_responses
from webtronics_social_network.server.core.auth import get_user
from webtronics_social_network.database.postgres.holder import PostgresHolder
from webtronics_social_network.types import errors

router = APIRouter(responses=user_auth_responses, dependencies=[Depends(get_user)])


@router.get("/", response_model=list[types.Post])
async def read_all(
        offset: int = 0,
        limit: int = 5,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker)
):
    posts = await pg_holder.post.read_all(offset=offset, limit=limit)

    typed_posts: list[types.Post] = []

    for post in posts:
        reactions = await redis_holder.reaction.read_by_post_id(post_id=post.id)

        typed_post = types.Post.from_dto(post=post, reactions=reactions)

        typed_posts.append(typed_post)

    return typed_posts


@router.get(
    "/{id}",
    response_model=types.Post,
    responses={
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | errors.PostNotFound
        }
    }
)
async def read(
        id: uuid.UUID,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker)
):
    post = await pg_holder.post.read_by_id(post_id=id)

    if not post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    reactions = await redis_holder.reaction.read_by_post_id(post_id=post.id)

    return types.Post.from_dto(post=post, reactions=reactions)


@router.post("/", response_model=types.Post)
async def create(
        post_create: types.PostCreate,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        user: types.User = Depends(get_user)
):
    post = await pg_holder.post.create(
        title=post_create.title,
        body=post_create.body,
        creator_id=user.id
    )

    return types.Post.from_dto(post=post)


@router.put(
    "/{id}",
    response_model=types.Post,
    responses={
        HTTP_400_BAD_REQUEST: {
            "description": "Unable to update post error",
            "model": errors.UnableUpdatePost
        },
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | errors.PostNotFoundOrNotCreator
        }
    }
)
async def update(
        id: uuid.UUID,
        post_update: types.PostUpdate,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker),
        user: types.User = Depends(get_user)
):
    try:
        post = await pg_holder.post.update(
            post_id=id,
            creator_id=user.id,
            data=post_update.dict(exclude_unset=True)
        )
    except exceptions.UnableInteraction:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Unable to update post"
        )

    if not post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Post not found or you are not the creator of this post"
        )

    reactions = await redis_holder.reaction.read_by_post_id(post_id=post.id)

    return types.Post.from_dto(post=post, reactions=reactions)


@router.delete(
    "/{id}",
    response_model=types.Post,
    responses={
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | errors.PostNotFoundOrNotCreator
        }
    }
)
async def delete(
        id: uuid.UUID,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker),
        user: types.User = Depends(get_user)
):
    post = await pg_holder.post.delete(post_id=id, creator_id=user.id)

    if not post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Post not found or you are not the creator of this post"
        )

    await redis_holder.reaction.delete_by_post_id(post_id=post.id)

    return types.Post.from_dto(post=post)

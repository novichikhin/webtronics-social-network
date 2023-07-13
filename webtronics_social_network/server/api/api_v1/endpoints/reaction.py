import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_200_OK

from webtronics_social_network import types
from webtronics_social_network.server.api.api_v1.dependencies.database.postgres import PostgresHolderMarker
from webtronics_social_network.server.api.api_v1.dependencies.database.redis import RedisHolderMarker
from webtronics_social_network.server.api.api_v1.responses.user import user_auth_responses
from webtronics_social_network.server.core.auth import get_user
from webtronics_social_network.database.postgres.holder import PostgresHolder
from webtronics_social_network.database.redis.holder import RedisHolder
from webtronics_social_network.types import errors

router = APIRouter(responses=user_auth_responses, dependencies=[Depends(get_user)])


@router.get("/{post_id}", response_model=list[types.Reaction])
async def read(post_id: uuid.UUID, redis_holder: RedisHolder = Depends(RedisHolderMarker)):
    reactions = await redis_holder.reaction.read_by_post_id(post_id=post_id)

    return [types.Reaction.from_dto(reaction=reaction) for reaction in reactions]


@router.post(
    "/",
    response_model=types.Reaction,
    responses={
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | errors.PostNotFound
        },
        HTTP_403_FORBIDDEN: {
            "description": "You can only post reactions to other people's posts error",
            "model": errors.CanOnlyPostReactionsOtherPeoplesPosts
        }
    }
)
async def create(
        reaction_create: types.ReactionCreate,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker),
        user: types.User = Depends(get_user)
):
    post = await pg_holder.post.read_by_id(post_id=reaction_create.post_id)

    if not post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    """
    if post.creator_id == user.id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You can only post reactions to other people's posts"
        )
    """

    reaction = await pg_holder.reaction.create(
        post_id=reaction_create.post_id,
        user_id=user.id,
        type=reaction_create.type
    )

    await redis_holder.reaction.create(
        reaction_id=reaction.id,
        post_id=reaction_create.post_id,
        user_id=user.id,
        type=reaction_create.type
    )

    return types.Reaction.from_dto(reaction=reaction)


@router.delete(
    "/{post_id}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {
            "model": user_auth_responses[HTTP_404_NOT_FOUND]["model"] | errors.ReactionNotFound
        }
    }
)
async def delete(
        post_id: uuid.UUID,
        pg_holder: PostgresHolder = Depends(PostgresHolderMarker),
        redis_holder: RedisHolder = Depends(RedisHolderMarker),
        user: types.User = Depends(get_user)
):
    reaction = await pg_holder.reaction.delete(post_id=post_id, user_id=user.id)

    if not reaction:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )

    await redis_holder.reaction.delete(
        reaction_id=reaction.id,
        post_id=post_id,
        user_id=user.id
    )

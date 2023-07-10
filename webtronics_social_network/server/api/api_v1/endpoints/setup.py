from fastapi import APIRouter

from webtronics_social_network.server.api.api_v1.endpoints import (
    user,
    post,
    reaction
)


def register_routers() -> APIRouter:
    router = APIRouter()

    router.include_router(
        user.router,
        prefix="/user",
        tags=["user"]
    )

    router.include_router(
        post.router,
        prefix="/post",
        tags=["post"]
    )

    router.include_router(
        reaction.router,
        prefix="/reaction",
        tags=["reaction"]
    )

    return router

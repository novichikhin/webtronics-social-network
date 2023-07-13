import uuid

import sqlalchemy as sa

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from webtronics_social_network import dto, exceptions
from webtronics_social_network.database.postgres import models
from webtronics_social_network.database.postgres.repositories.main import PostgresRepository


class PostRepository(PostgresRepository[models.Post]):

    def __init__(self, session: AsyncSession):
        super().__init__(model=models.Post, session=session)

    async def read_all(self, offset: int, limit: int) -> list[dto.Post]:
        posts = await self._read_all(offset=offset, limit=limit)

        return [post.to_dto() for post in posts]

    async def read_by_id(self, post_id: uuid.UUID) -> Optional[dto.Post]:
        post = await self._read_by_id(id=post_id)

        return post.to_dto() if post else None

    async def update(
            self,
            post_id: uuid.UUID,
            creator_id: uuid.UUID,
            data: dict
    ) -> Optional[dto.Post]:
        try:
            post: Optional[models.Post] = await self._update(
                models.Post.id == post_id,
                models.Post.creator_id == creator_id,
                **data
            )
        except IntegrityError as e:
            await self._session.rollback()
            raise exceptions.UnableInteraction from e
        else:
            return post.to_dto() if post else None

    async def create(
            self,
            title: str,
            body: str,
            creator_id: uuid.UUID
    ) -> dto.Post:
        stmt = sa.insert(models.Post).values(
            title=title,
            body=body,
            creator_id=creator_id
        ).returning(models.Post)

        result: sa.ScalarResult[models.Post] = await self._session.scalars(
            sa.select(models.Post).from_statement(stmt)
        )
        await self._session.commit()

        return (post := result.one()).to_dto()

    async def delete(
            self,
            post_id: uuid.UUID,
            creator_id: uuid.UUID
    ) -> Optional[dto.Post]:
        post: Optional[models.Post] = await self._delete(
            models.Post.id == post_id,
            models.Post.creator_id == creator_id
        )

        return post.to_dto() if post else None

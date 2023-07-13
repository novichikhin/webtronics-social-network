import uuid

import sqlalchemy as sa

from typing import Optional, Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from webtronics_social_network import dto, enums
from webtronics_social_network.database.postgres import models
from webtronics_social_network.database.postgres.repositories.main import PostgresRepository


class ReactionRepository(PostgresRepository[models.Reaction]):

    def __init__(self, session: AsyncSession):
        super().__init__(model=models.Reaction, session=session)

    async def read_by_post_id(self, post_id: uuid.UUID) -> list[dto.Reaction]:
        result: sa.ScalarResult[models.Reaction] = await self._session.scalars(
            sa.select(models.Reaction).where(
                models.Reaction.post_id == post_id
            )
        )

        reactions: Sequence[models.Reaction] = result.all()

        return [reaction.to_dto() for reaction in reactions]

    async def create(
            self,
            post_id: uuid.UUID,
            user_id: uuid.UUID,
            type: enums.ReactionType
    ) -> dto.Reaction:
        stmt = insert(models.Reaction).values(
            post_id=post_id,
            user_id=user_id,
            type=type
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                models.Reaction.user_id,
                models.Reaction.post_id
            ],
            set_=dict(
                type=stmt.excluded.type
            )
        ).returning(models.Reaction)

        result: sa.ScalarResult[models.Reaction] = await self._session.scalars(
            sa.select(models.Reaction).from_statement(stmt)
        )
        await self._session.commit()

        return (reaction := result.one()).to_dto()

    async def delete(
            self,
            post_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Optional[dto.Reaction]:
        reaction: Optional[models.Reaction] = await self._delete(
            models.Reaction.post_id == post_id,
            models.Reaction.user_id == user_id
        )

        return reaction.to_dto() if reaction else None

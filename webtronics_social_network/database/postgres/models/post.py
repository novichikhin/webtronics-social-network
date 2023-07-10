import datetime as dt
import uuid
import sqlalchemy as sa

import sqlalchemy.orm as so
import uuid6

from webtronics_social_network import dto
from webtronics_social_network.database.postgres.models import User
from webtronics_social_network.database.postgres.models.main import PostgresBase


class Post(PostgresBase):
    __tablename__ = "posts"

    id: so.Mapped[uuid.UUID] = so.mapped_column(primary_key=True, default=uuid6.uuid7)
    title: so.Mapped[str] = so.mapped_column(nullable=False)
    body: so.Mapped[str] = so.mapped_column(nullable=False)
    created_at: so.Mapped[dt.datetime] = so.mapped_column(nullable=False, default=dt.datetime.utcnow)

    creator_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    creator: so.Mapped["User"] = so.relationship()

    def to_dto(self) -> dto.Post:
        return dto.Post(
            id=self.id,
            title=self.title,
            body=self.body,
            created_at=self.created_at,
            creator_id=self.creator_id
        )

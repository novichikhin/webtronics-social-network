import uuid
import datetime as dt

import sqlalchemy.orm as so

import uuid6

from webtronics_social_network import dto
from webtronics_social_network.database.postgres.models.main import PostgresBase


class User(PostgresBase):
    __tablename__ = "users"

    id: so.Mapped[uuid.UUID] = so.mapped_column(primary_key=True, default=uuid6.uuid7)
    username: so.Mapped[str] = so.mapped_column(nullable=False, unique=True)
    password: so.Mapped[str] = so.mapped_column(nullable=False)
    created_at: so.Mapped[dt.datetime] = so.mapped_column(nullable=False, default=dt.datetime.utcnow)

    def to_dto(self) -> dto.User:
        return dto.User(
            id=self.id,
            username=self.username,
            password=self.password,
            created_at=self.created_at
        )

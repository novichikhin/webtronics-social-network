import uuid
import sqlalchemy as sa

import sqlalchemy.orm as so
import uuid6

from webtronics_social_network import dto, enums
from webtronics_social_network.database.postgres.models.main import PostgresBase


class Reaction(PostgresBase):
    __tablename__ = "reactions"
    __table_args__ = (sa.UniqueConstraint("user_id", "post_id", name="reactions_user_post"),)

    id: so.Mapped[uuid.UUID] = so.mapped_column(primary_key=True, default=uuid6.uuid7)

    user_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    type: so.Mapped[enums.ReactionType] = so.mapped_column(nullable=False)

    def to_dto(self) -> dto.Reaction:
        return dto.Reaction(
            id=self.id,
            user_id=self.user_id,
            post_id=self.post_id,
            type=self.type
        )

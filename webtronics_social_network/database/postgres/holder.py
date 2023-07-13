from sqlalchemy.ext.asyncio import AsyncSession

from webtronics_social_network.database.postgres.repositories.post import PostRepository
from webtronics_social_network.database.postgres.repositories.reaction import ReactionRepository
from webtronics_social_network.database.postgres.repositories.user import UserRepository


class PostgresHolder:

    def __init__(self, session: AsyncSession):
        self.user = UserRepository(session=session)
        self.post = PostRepository(session=session)
        self.reaction = ReactionRepository(session=session)

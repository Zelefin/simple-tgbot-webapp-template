from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.users import UserRepo
from infrastructure.database.models.base import Base


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)


class Database:
    def __init__(self, engine):
        self.engine = engine

    async def create_tables(self):
        # Async function to create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

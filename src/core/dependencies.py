from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from src.database.db import new_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session
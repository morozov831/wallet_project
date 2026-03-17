from decimal import Decimal

from main import app
import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator

from src.core.dependencies import get_db
from src.database.models import Base, Wallet

engine = create_async_engine(url=settings.TEST_DATABASE_URL)
new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

@pytest.fixture
async def test_wallet():
    async with new_session() as session:
        wallet = Wallet(balance=Decimal('1000.00'))
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)
        yield wallet


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
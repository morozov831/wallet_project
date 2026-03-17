import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Wallet
from sqlalchemy import select


async def get_wallet(
        db: AsyncSession,
        wallet_uuid: uuid.UUID
) -> Wallet:
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_uuid)
    )
    wallet = result.scalar_one_or_none()
    return wallet or None

async def get_wallet_for_update(
        db: AsyncSession,
        wallet_uuid: uuid.UUID
) -> Wallet:
    result = await db.execute(
        select(Wallet)
        .where(Wallet.id == wallet_uuid)
        .with_for_update()
    )
    wallet = result.scalar_one_or_none()
    return wallet or None

async def save_wallet(
        db: AsyncSession,
        wallet: Wallet
) -> None:
    db.add(wallet)
    await db.flush()
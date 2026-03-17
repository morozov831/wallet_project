from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InsufficientFundsError, WalletNotFoundError
from src.database.repositories import get_wallet_for_update, save_wallet, get_wallet


async def get_balance(
    db: AsyncSession,
    wallet_uuid: uuid.UUID
) -> Decimal:
    wallet = await get_wallet(db, wallet_uuid)
    if not wallet:
        raise WalletNotFoundError()
    return wallet.balance

async def deposit_to_wallet(
        db: AsyncSession,
        wallet_uuid: uuid.UUID,
        amount: Decimal
) -> Decimal:

    wallet = await get_wallet_for_update(db, wallet_uuid)

    if not wallet:
        raise WalletNotFoundError()

    wallet.balance += amount
    await save_wallet(db, wallet)

    return wallet.balance


async def withdraw_from_wallet(
        db: AsyncSession,
        wallet_uuid: uuid.UUID,
        amount: Decimal
) -> Decimal:

    wallet = await get_wallet_for_update(db, wallet_uuid)

    if not wallet:
        raise WalletNotFoundError()
    if wallet.balance < amount:
        raise InsufficientFundsError()

    wallet.balance -= amount
    await save_wallet(db, wallet)

    return wallet.balance
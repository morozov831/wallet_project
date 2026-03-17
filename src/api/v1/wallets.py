from typing import Annotated
from fastapi import HTTPException, status, Depends, Path, APIRouter
from src.core.dependencies import get_db
from src.core.exceptions import WalletNotFoundError, InsufficientFundsError, NegativeBalanceError
from src.schemas import WalletOperationRequest, OperationType
from src.services import deposit_to_wallet, withdraw_from_wallet, get_balance
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

wallets_router = APIRouter(prefix='/wallets', tags=['Wallets'])


@wallets_router.get('/{wallet_uuid}')
async def get_wallet_balance(
        wallet_uuid: Annotated[
            uuid.UUID,
            Path(description="UUID кошелька", example="71767b2f-9ac0-403e-ab2c-eb6a6c72da87")
        ],
        db: AsyncSession = Depends(get_db)
):
    try:
        balance = await get_balance(db, wallet_uuid)
        return {'data': {'balance': f"{balance:.2f}"}}
    except WalletNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@wallets_router.post('/{wallet_uuid}/operation')
async def process_wallet_operation(
        wallet_uuid: Annotated[
            uuid.UUID,
            Path(description="UUID кошелька", example="71767b2f-9ac0-403e-ab2c-eb6a6c72da87")
        ],
        operation: WalletOperationRequest,
        db: AsyncSession = Depends(get_db),
):
    try:
        if operation.operation_type == OperationType.DEPOSIT:
            balance = await deposit_to_wallet(
                db,
                wallet_uuid=wallet_uuid,
                amount=operation.amount
            )
        else:
            balance = await withdraw_from_wallet(
                db,
                wallet_uuid=wallet_uuid,
                amount=operation.amount
            )
        await db.commit()
        return {'data': {'balance': f"{balance:.2f}"}}

    except (WalletNotFoundError, InsufficientFundsError, NegativeBalanceError) as e:
        await db.rollback()
        if isinstance(e, WalletNotFoundError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кошелек не найден")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно средств на кошельке")
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

import asyncio
import uuid
from decimal import Decimal
from sqlalchemy import delete
from src.database.db import new_session
from src.database.models import Wallet

async def clear_wallets(db):
    await db.execute(delete(Wallet))
    await db.commit()
    print("Таблица wallets очищена")

async def create_wallets():
    async with new_session() as db:
        await clear_wallets(db)
        test_wallets = {
            uuid.UUID('f5db6a18-f29b-46e8-847b-b443a0250db1'): Decimal('1000.00'),
            uuid.UUID('71767b2f-9ac0-403e-ab2c-eb6a6c72da87'): Decimal('500.50'),
            uuid.UUID('9a5523d4-0346-4edc-90f4-b67eec63e434'): Decimal('10000.00'),
            uuid.UUID('24a3860d-df1b-47fc-8d27-baf100dacb4e'): Decimal('0.00'),
            uuid.UUID('4e8e2ca7-5a68-40fa-a568-44ccd3feff1b'): Decimal('999999.99')
        }

        wallets = []
        for wallet_id, balance in test_wallets.items():
            from sqlalchemy import select
            result = await db.execute(
                select(Wallet).where(Wallet.id == wallet_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                continue

            wallet = Wallet(
                id=wallet_id,
                balance=balance
            )
            db.add(wallet)
            wallets.append(wallet)

        await db.commit()

        print(f"\nСоздано {len(wallets)} кошельков:")
        for wallet in wallets:
            await db.refresh(wallet)
            print(f"{wallet.id} | баланс: {wallet.balance}")

        return [w.id for w in wallets]


if __name__ == '__main__':
    asyncio.run(create_wallets())
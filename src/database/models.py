from sqlalchemy.orm import DeclarativeBase, MappedColumn, Mapped, validates
from sqlalchemy import Numeric, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from decimal import Decimal

from src.core.exceptions import NegativeBalanceError


class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)
    balance: Mapped[Decimal] = MappedColumn(
        Numeric(scale=2),
        nullable=False,
        default=0.00
    )
    created_at = MappedColumn(
        DateTime(timezone=True),
        server_default=func.now()
    )

    @validates('balance')
    def validate_balance(self, key, value):
        if value < 0:
            raise NegativeBalanceError()
        return value
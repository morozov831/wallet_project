from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class WalletOperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation_type": "DEPOSIT",
                    "amount": 100.50
                },
                {
                    "operation_type": "WITHDRAW",
                    "amount": 50.25
                }
            ]
        }
    }
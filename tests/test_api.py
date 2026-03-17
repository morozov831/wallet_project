from httpx import AsyncClient
from decimal import Decimal
import uuid
import asyncio


async def test_get_wallet_balance_success(ac: AsyncClient, test_wallet):
    """GET /wallets/{uuid} - успех"""
    response = await ac.get(f"/api/v1/wallets/{test_wallet.id}")

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["data"]["balance"])) == test_wallet.balance


async def test_get_wallet_balance_not_found(ac: AsyncClient):
    """GET /wallets/{uuid} - не найден"""
    non_existent_uuid = uuid.uuid4()
    response = await ac.get(f"/api/v1/wallets/{non_existent_uuid}")

    assert response.status_code == 404


async def test_deposit_success(ac: AsyncClient, test_wallet):
    """POST /wallets/{uuid}/operation - пополнение"""
    initial_balance = test_wallet.balance
    deposit_amount = Decimal('100.50')

    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": float(deposit_amount)
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["data"]["balance"])) == initial_balance + deposit_amount


async def test_withdraw_success(ac: AsyncClient, test_wallet):
    """POST /wallets/{uuid}/operation - снятие"""
    initial_balance = test_wallet.balance
    withdraw_amount = Decimal('50.25')

    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": float(withdraw_amount)
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["data"]["balance"])) == initial_balance - withdraw_amount


async def test_withdraw_insufficient_funds(ac: AsyncClient, test_wallet):
    """POST /wallets/{uuid}/operation - недостаточно средств"""
    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": float(test_wallet.balance) + 100
        }
    )

    assert response.status_code == 400


async def test_operation_invalid_amount(ac: AsyncClient, test_wallet):
    """POST /wallets/{uuid}/operation - невалидная сумма"""
    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": -100
        }
    )

    assert response.status_code == 422


async def test_operation_invalid_type(ac: AsyncClient, test_wallet):
    """POST /wallets/{uuid}/operation - невалидный тип"""
    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "INVALID",
            "amount": 100
        }
    )

    assert response.status_code == 422


async def test_operation_wallet_not_found(ac: AsyncClient):
    """POST /wallets/{uuid}/operation - кошелек не найден"""
    non_existent_uuid = uuid.uuid4()
    response = await ac.post(
        f"/api/v1/wallets/{non_existent_uuid}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": 100
        }
    )

    assert response.status_code == 404


async def test_concurrent_deposits(ac: AsyncClient, test_wallet):
    """5 конкурентных пополнений"""
    initial_balance = test_wallet.balance
    deposit_amount = 100

    async def make_deposit():
        return await ac.post(
            f"/api/v1/wallets/{test_wallet.id}/operation",
            json={"operation_type": "DEPOSIT", "amount": deposit_amount}
        )

    tasks = [make_deposit() for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200

    response = await ac.get(f"/api/v1/wallets/{test_wallet.id}")
    final_balance = Decimal(str(response.json()["data"]["balance"]))
    expected = initial_balance + (deposit_amount * 5)
    assert final_balance == expected


async def test_concurrent_withdrawals(ac: AsyncClient, test_wallet):
    """5 конкурентных снятий"""
    initial_balance = test_wallet.balance
    withdraw_amount = 100

    async def make_withdraw():
        return await ac.post(
            f"/api/v1/wallets/{test_wallet.id}/operation",
            json={"operation_type": "WITHDRAW", "amount": withdraw_amount}
        )

    tasks = [make_withdraw() for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200

    response = await ac.get(f"/api/v1/wallets/{test_wallet.id}")
    final_balance = Decimal(str(response.json()["data"]["balance"]))
    expected = initial_balance - (withdraw_amount * 5)
    assert final_balance == expected


async def test_concurrent_mixed_operations(ac: AsyncClient, test_wallet):
    """Смешанные конкурентные операции"""
    initial_balance = test_wallet.balance

    async def deposit():
        return await ac.post(
            f"/api/v1/wallets/{test_wallet.id}/operation",
            json={"operation_type": "DEPOSIT", "amount": 100}
        )

    async def withdraw():
        return await ac.post(
            f"/api/v1/wallets/{test_wallet.id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 50}
        )

    tasks = [deposit() for _ in range(3)] + [withdraw() for _ in range(2)]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200

    response = await ac.get(f"/api/v1/wallets/{test_wallet.id}")
    final_balance = Decimal(str(response.json()["data"]["balance"]))
    expected = initial_balance + (100 * 3) - (50 * 2)
    assert final_balance == expected


async def test_withdraw_all_funds(ac: AsyncClient, test_wallet):
    """Снятие всех средств"""
    withdraw_amount = float(test_wallet.balance)

    response = await ac.post(
        f"/api/v1/wallets/{test_wallet.id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": withdraw_amount
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["data"]["balance"])) == Decimal('0')
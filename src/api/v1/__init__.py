from fastapi import APIRouter
from .wallets import wallets_router

api_v1 = APIRouter(prefix='/api/v1')
api_v1.include_router(wallets_router)
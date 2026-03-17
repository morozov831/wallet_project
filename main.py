from fastapi import FastAPI
from src.api.v1 import api_v1


app = FastAPI(title="Wallet API")

@app.get('/')
async def root():
    return {"message": "Wallet API", "docs": "/docs"}


app.include_router(api_v1)
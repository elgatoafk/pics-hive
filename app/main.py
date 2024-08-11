import asyncio
import sys
import os
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import event, select
from sqlalchemy.exc import DisconnectionError
from app.src.util.db import async_engine, init_db

from app.src.config.fastapi_config import app
from app.src.util.crud.token import remove_expired_tokens, remove_blacklisted_tokens

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')


scheduler = AsyncIOScheduler()

scheduler.add_job(remove_expired_tokens, 'interval', minutes=30)
scheduler.add_job(remove_blacklisted_tokens, 'interval', minutes=30)

scheduler.start()


@app.on_event("startup")
async def on_startup():
    await init_db()


@event.listens_for(async_engine.sync_engine, "connect")
async def test_connection(connection, branch):
    if branch:
        return
    try:
        await connection.scalar(select(1))
    except DisconnectionError:
        await connection.scalar(select(1))


# Run the application
if __name__ == "__main__":
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=debug_mode)

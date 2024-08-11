import asyncio
import sys
import os
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy import event, select
from sqlalchemy.exc import DisconnectionError
from starlette.responses import FileResponse
from app.src.config.exceptions import custom_http_exception_handler, global_exception_handler, \
    validation_exception_handler, custom_404_handler
from app.src.routes import auth, user, photo, comment, rating, root, templating, admin_templating
from app.src.util.db import Base, async_engine
from app.src.config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from apscheduler.schedulers.background import BackgroundScheduler

from app.src.util.crud.token import remove_expired_tokens, remove_blacklisted_tokens

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

#schedule token cleanup
scheduler = AsyncIOScheduler()

scheduler.add_job(remove_expired_tokens, 'interval', minutes=30)
scheduler.add_job(remove_blacklisted_tokens, 'interval', minutes=30)

scheduler.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


# Include API routers
app.include_router(root.router, prefix="", tags=["root"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="", tags=["users"])
app.include_router(photo.router, prefix="", tags=["photos"])
app.include_router(comment.router, prefix="", tags=["comments"])
app.include_router(rating.router, prefix="", tags=["ratings"])
app.include_router(templating.router, prefix="", tags=["front-end"])
app.include_router(admin_templating.router, prefix="", tags=["admin front"])

app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, custom_404_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)

app.mount("/static", StaticFiles(directory="app/src/static"), name="static")


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("app/src/static/favicon.png")


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
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=debug_mode)

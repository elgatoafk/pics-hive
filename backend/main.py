import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

import uvicorn
import logging
from fastapi import FastAPI
from src.routes import auth, user, photo, comment, tag, rating
from backend.src.util.db import engine
from backend.src.util.models.base import Base
import cloudinary
from backend.src.config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# Ensure correct PYTHONPATH



app = FastAPI(
    title = settings.PROJECT_NAME,
    description = settings.DESCRIPTION,
    version = settings.VERSION
)

# CORS Middleware setup, adjust as necessary
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create database tables
#Base.metadata.drop_all(bind=engine)
#Base.metadata.create_all(bind=engine)

DATABASE_URL = settings.DATABASE_URL 

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)



# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Database initialization

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include API routers
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(user.router, prefix="", tags=["users"])
app.include_router(photo.router, prefix="/photos", tags=["photos"])
app.include_router(comment.router, prefix="/comments", tags=["comments"])
app.include_router(tag.router, prefix="/tags", tags=["tags"])
app.include_router(rating.router, prefix="/ratings", tags=["ratings"])

# Root endpoint

@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}


@app.on_event("startup")
async def on_startup():
    await init_db()


# Run the application
if __name__ == "__main__":
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=debug_mode)


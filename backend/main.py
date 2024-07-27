import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from fastapi import FastAPI
from src.routes import auth, user, photo, comment, tag, rating
from src.util.db import engine
from backend.src.util.models.base import Base

import cloudinary
from src.config.config import settings

from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)


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

# Include API routers
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(user.router, prefix="", tags=["users"])
app.include_router(photo.router, prefix="", tags=["photos"])
app.include_router(comment.router, prefix="", tags=["comments"])
app.include_router(tag.router, prefix="", tags=["tags"])
#app.include_router(rating.router, prefix="/ratings", tags=["ratings"])


@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}

if __name__ == "__main__":
    import uvicorn
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=debug_mode)







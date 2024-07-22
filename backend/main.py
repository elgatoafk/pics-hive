import sys
import os

#from backend.src.routes import ddddauth

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from fastapi import FastAPI
from src.routes import user, photo, comment, tag, rating
from src.util.db import engine  #, Base
#from src.util.models import models
from src.util.models.models import Base

import cloudinary
from src.config.config import settings

cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)


app = FastAPI()


# Create database tables
#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Include API routers
#app.include_router(auth.router, prefix="/auth", tags=["auth"])
#app.include_router(user.router)
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


from fastapi import FastAPI
from src.routes import auth, user, photo, comment, tag, rating
from src.util.db import engine, Base


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(photo.router, prefix="/photos", tags=["photos"])
app.include_router(comment.router, prefix="/comments", tags=["comments"])
app.include_router(tag.router, prefix="/tags", tags=["tags"])
app.include_router(rating.router, prefix="/ratings", tags=["ratings"])

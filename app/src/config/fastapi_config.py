import os

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.exceptions import RequestValidationError
from starlette.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from app.src.config.config import settings
from app.src.config.exceptions import custom_http_exception_handler, global_exception_handler, \
    validation_exception_handler, \
    custom_404_handler, custom_401_handler
from app.src.routes import root, auth, user, photo, comment, rating, templating, admin_templating
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION, docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
              redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc"
)

origins = [
    "http://127.0.0.1:8000",
    "https://loose-paule-logicforge-b366e4a4.koyeb.app/",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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
app.add_exception_handler(HTTPException, custom_401_handler)

static_directory = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/static", StaticFiles(directory=static_directory), name="static")


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(f"{static_directory}/favicon.png")

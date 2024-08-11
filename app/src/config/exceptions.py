from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from app.src.config.config import templates, FrontEndpoints, url_to_endpoint
import urllib.parse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch all unhandled exceptions and show a custom 500 error page.
    """

    return templates.TemplateResponse("500.html", {"request": request},
                                      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error['loc'][0] == 'path':
            return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("error.html", {"request": request, "detail": exc.errors(), "status_code": 422})


async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles 404 errors by rendering a custom 404.html template.

    Args:
        request (Request): The HTTP request object.
        exc (StarletteHTTPException): The HTTP exception instance.

    Returns:
        TemplateResponse: The rendered 404 error page.
    """
    return templates.TemplateResponse("404.html", {"request": request}, status_code=status.HTTP_404_NOT_FOUND)

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions with routing logic based on the request path.

    Args:
        request (Request): The HTTP request object.
        exc (HTTPException): The HTTP exception that occurred.

    Returns:
        RedirectResponse: Redirects to the appropriate GET endpoint with an error message.
    """
    error_message = urllib.parse.quote(exc.detail)
    for key, endpoint in url_to_endpoint.items():
        if key in request.url.path:
            return RedirectResponse(url=f"{endpoint}?error={error_message}", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"{FrontEndpoints.HOME.value}?error={error_message}",
                            status_code=status.HTTP_302_FOUND)

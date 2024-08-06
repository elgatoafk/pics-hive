from fastapi import APIRouter, Response, status
router = APIRouter()


@router.get("/")
async def root():
    return Response(content="Find a coffeemaker", status_code=status.HTTP_418_IM_A_TEAPOT, media_type="text/plain")
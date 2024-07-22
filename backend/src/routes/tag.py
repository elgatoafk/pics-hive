from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.util.schemas.tag import TagCreate, TagResponse
from backend.src.util.crud.tag import create_tag, get_tag, update_tag, delete_tag
from backend.src.util.db import get_db

router = APIRouter()

@router.post("/tags/", response_model=TagResponse)
async def create_tag_route(tag: TagCreate, db: Session = Depends(get_db)):
    return await create_tag(db, tag)

@router.get("/tags/", response_model=TagResponse)
async def get_tag_route(tag_name: str, db: Session = Depends(get_db)):
    return await get_tag(db, tag_name)

@router.put("/tags/", response_model=TagResponse)
async def update_tag_route(tag: TagCreate, tag_id: int, db: Session = Depends(get_db)):
    tag_updated = await update_tag(tag, tag_id, db)
    if not tag_updated:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag_updated

@router.delete("/tags/", response_model=TagResponse)
async def delete_tag_route(tag_name: str, db: Session = Depends(get_db)):
    tag_db = await get_tag(tag_name, db)
    if not tag_db:
        raise HTTPException(status_code=404, detail="Tag not found")
    else:
        await delete_tag(tag_db, db)
        return {"detail": "Tag deleted successfully"}
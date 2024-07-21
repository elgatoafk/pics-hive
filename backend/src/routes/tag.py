from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.util.schemas.tag import TagCreate, TagResponse
from backend.src.util.crud.tag import create_tag, get_tag, update_tag, delete_tag
from backend.src.util.db import get_db

router = APIRouter()

@router.post("/tags/", response_model=TagResponse)
async def create_tag_route(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = create_tag(db, tag)
    return new_tag

@router.get("/tags/", response_model=TagResponse)
async def get_tags_route(db: Session = Depends(get_db)):
    pass

@router.put("/tags/", response_model=TagResponse)
async def update_tag_route(tag: TagCreate, tag_id: int, db: Session = Depends(get_db)):
    tag_updated = update_tag(tag, tag_id, db)
    if not tag_updated:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag_updated
@router.delete("/tags/", response_model=TagResponse)
async def delete_tag_route():
    pass
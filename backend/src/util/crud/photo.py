import bcrypt
from sqlalchemy.orm import Session
from backend.src.util.schemas import photo
from backend.src.util.models import models


def create_photo(db: Session, photo: photo.PhotoCreate, user_id: int):
    print('create_photo')
    db_photo = models.Photo(
        url=photo.url,
        description=photo.description,
        owner_id=user_id
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    print('commit test')

    print(photo.tags)

    for tag_create in photo.tags or []:
        tag_name = tag_create.name  # Access the tag name from TagCreate
        db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not db_tag:
            db_tag = models.Tag(name=tag_name)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        db_photo.tags.append(db_tag)
        db.commit()

    # Return a response model with tag names
    response_photo = photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )

    print('crate_photo completed')
    return response_photo



def get_photo(db: Session, photo_id: int):
    if dbg: print('get_photo')
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if not db_photo:
        return None

    # Return a response model with tag names
    response_photo = photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )
    return response_photo



def update_photo(db: Session, photo_id: int, photo_update: photo.PhotoCreate):
    if dbg: print('update_photo')

    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if not db_photo:
        return None

    db_photo.url = photo_update.url
    db_photo.description = photo_update.description

    # Clear existing tags
    db_photo.tags = []

    # Add new tags
    for tag_create in photo_update.tags or []:
        tag_name = tag_create.name
        db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not db_tag:
            db_tag = models.Tag(name=tag_name)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        db_photo.tags.append(db_tag)
    db.commit()
    db.refresh(db_photo)

    # Return a response model with tag names
    response_photo = photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )

    print('update_photo completed')
    return response_photo

def delete_photo(db: Session, photo_id: int):
    if dbg: print('delete_photo')
    if dbg: print('photo_id : {}'.format(photo_id))
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if db_photo:
        db.delete(db_photo)
        db.commit()



def transform_photo(db: Session, db_photo: models.Photo, transformation: str) -> photo.Photo:
    if transformation == "scale":
        # Example transformation logic
        db_photo.url += "?transformation=scale"
    elif transformation == "r_max":
        # Example transformation logic for r_max
        db_photo.url += "?transformation=r_max"
    else:
        raise ValueError("Invalid transformation")

    # Commit the changes to the database
    db.commit()
    db.refresh(db_photo)

    # Convert ORM model instance to Pydantic schema
    response_photo = photo.Photo.from_orm(db_photo)

    return response_photo
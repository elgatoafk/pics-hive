from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import settings
#from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

#Base = declarative_base()  ## fix it is in models.
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#def get_db():
#    db = SessionLocal()
#    try:
#        yield db
#    finally:
#        db.close()

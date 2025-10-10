from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config.settings import DB_URL

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)







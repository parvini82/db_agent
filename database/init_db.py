from data.seed_data import seed_data
from database.models import Base
from database.connection import engine,sessionmaker

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    seed_data()
if __name__ == "__main__":
    init_db()
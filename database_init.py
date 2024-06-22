from sqlalchemy import create_engine
from models import Base

# Use an absolute path to the SQLite database
DATABASE_URL = 'sqlite:///tippspiel.db'
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

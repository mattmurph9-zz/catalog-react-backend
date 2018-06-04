from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import engine_str
from database_setup import Base

engine = create_engine(engine_str)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

from decouple import config
from models import *
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

URL = config('URL', default='')
engine = create_engine({URL})
connection = engine.connect()
session = Session(bind=engine)
metadata = MetaData(engine)
Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_db()

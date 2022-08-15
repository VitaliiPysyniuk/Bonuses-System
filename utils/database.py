import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import database_exists, create_database


def build_db_url():
    pg_user = os.environ.get('POSTGRES_USER')
    pg_password = os.environ.get('POSTGRES_PASSWORD')
    pg_host = os.environ.get('POSTGRES_HOST')
    pg_port = os.environ.get('POSTGRES_PORT')
    pg_db = os.environ.get('POSTGRES_DB')

    url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

    return url


def create_db_engine():
    db_url = build_db_url()
    engine = create_engine(db_url)

    try:
        if not database_exists(engine.url):
            create_database(engine.url)
        else:
            engine.connect()
    except OperationalError:
        print(f'Connection failed: {db_url}')
        return None

    return engine


def open_db_session():
    engine = create_db_engine()
    session = Session(engine)

    return session


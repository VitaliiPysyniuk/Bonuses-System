import os
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models.models import Base


def build_test_db_url():
    load_dotenv('.env.test')

    pg_user = os.environ.get('POSTGRES_USER')
    pg_password = os.environ.get('POSTGRES_PASSWORD')
    pg_host = os.environ.get('POSTGRES_HOST')
    pg_port = os.environ.get('POSTGRES_PORT')
    pg_db = os.environ.get('POSTGRES_DB')

    url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

    return url


@pytest.fixture(scope='session')
def engine():
    test_db_url = build_test_db_url()
    engine = sa.create_engine(test_db_url)

    return engine


@pytest.fixture(scope='session')
def connection(engine):
    connection = engine.connect()

    yield connection

    connection.close()


@pytest.fixture()
def clear_db(connection, engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    connection.execute('ALTER SEQUENCE bonuses_types_id_seq RESTART WITH 1')
    connection.execute('ALTER SEQUENCE workers_id_seq RESTART WITH 1')
    connection.execute('ALTER SEQUENCE roles_id_seq RESTART WITH 1')
    connection.execute('ALTER SEQUENCE workers_roles_relations_id_seq RESTART WITH 1')
    connection.execute('ALTER SEQUENCE requests_id_seq RESTART WITH 1')
    connection.execute('ALTER SEQUENCE requests_history_id_seq RESTART WITH 1')


@pytest.fixture()
def session(connection, clear_db, engine):
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()


import os

from utils.database import create_db_engine, build_db_url


def test_build_db_url():
    os.environ['POSTGRES_USER'] = 'pg_user'
    os.environ['POSTGRES_PASSWORD'] = 'pg_password'
    os.environ['POSTGRES_HOST'] = 'pg_host'
    os.environ['POSTGRES_PORT'] = 'pg_port'
    os.environ['POSTGRES_DB'] = 'pg_db'

    result = build_db_url()

    assert type(result) == str
    assert result == 'postgresql://pg_user:pg_password@pg_host:pg_port/pg_db'


def test_create_db_engine_with_wrong_db_url(mocker):
    mocker.patch('utils.database.build_db_url', return_value='postgresql://pg_user:pg_password@pg_host:0000/pg_db')

    result = create_db_engine()

    assert result is None

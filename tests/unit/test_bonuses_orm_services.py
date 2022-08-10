import pytest

from lambda_bonuses.orm_services import BonusesQuery
from models.models import Bonus

test_bonuses_data = [
    {'type': 'New Year', 'description': 'New Year bonus'},
    {'type': 'Newcomer', 'description': 'Newcomer bonus'},
    {'type': 'Birthday', 'description': 'Birthday bonus'},
    {'type': 'Annual', 'description': 'Annual bonus'}
]


@pytest.fixture()
def fill_bonuses_db(session):
    for bonus_data in test_bonuses_data:
        new_bonus = Bonus(**bonus_data)
        session.add(new_bonus)
        session.commit()


def test_get_bonuses_query_with_empty_db(mocker, session):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.get_bonuses()

    assert type(result) is list
    assert len(result) == 0


def test_get_bonuses_query_with_not_empty_db(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.get_bonuses()

    assert type(result) is list
    assert len(result) == len(test_bonuses_data)


def test_get_bonus_by_id_query_with_existing_bonus(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.get_bonus_by_id(1)

    assert type(result) is dict
    assert result['id'] == 1
    assert result['type'] == test_bonuses_data[0]['type']


def test_get_bonus_by_id_query_with_not_existing_bonus(mocker, session):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.get_bonus_by_id(1)

    assert result == 0


def test_get_bonus_by_id_query_with_not_correct_id(mocker, session):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.get_bonus_by_id('one')

    assert result == 0


def test_add_bonus_query(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)
    bonus_data = {'type': 'Overtime', 'description': 'Overtime'}

    result = BonusesQuery.add_new_bonus(bonus_data)

    assert type(result) is dict
    assert result['id'] == len(test_bonuses_data) + 1
    assert result['type'] == bonus_data['type']


def test_add_bonus_query_when_bonus_already_exist(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)
    bonus_data = {'type': 'New Year', 'description': 'New Year bonus'}

    result = BonusesQuery.add_new_bonus(bonus_data)

    assert result == 0


def test_delete_bonus_query_with_existing_bonus(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result_1 = BonusesQuery.delete_bonus(1)
    result_2 = BonusesQuery.delete_bonus(2)
    result_3 = BonusesQuery.delete_bonus(3)

    assert result_1 == 1
    assert result_2 == 1
    assert result_3 == 1


def test_delete_bonus_query_with_not_existing_bonus(mocker, session):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.delete_bonus(1)

    assert result == 0


def test_delete_bonus_query_with_with_not_correct_id(mocker, session):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)

    result = BonusesQuery.delete_bonus('one')

    assert result == 0


def test_update_bonus_query_with_correct_data(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)
    bonus_data = {'type': 'Overtime', 'description': 'Overtime bonus'}

    result = BonusesQuery.update_bonus(1, bonus_data)

    assert type(result) is dict
    assert result['id'] == 1
    assert result['type'] == bonus_data['type']
    assert result['type'] != test_bonuses_data[0]['type']


def test_update_bonus_query_with_not_correct_data(mocker, session, fill_bonuses_db):
    mocker.patch('lambda_bonuses.orm_services.open_db_session', return_value=session)
    bonus_data = {'type': 'Newcomer'}

    result = BonusesQuery.update_bonus(1, bonus_data)

    assert result == 0


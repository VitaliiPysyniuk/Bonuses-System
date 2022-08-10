import pytest
from copy import deepcopy

from lambda_workers.orm_services import WorkersQuery
from models.models import Worker, Role, WorkersRolesRelation

test_role_data = [
    {'role_name': 'worker'},
    {'role_name': 'reviewer'},
    {'role_name': 'administrator'}
]

test_workers_data = [
    {'full_name': 'Roman Romanov', 'position': 'developer', 'slack_id': 'EF4ED73Q12X', 'roles': [1, 2, 3]},
    {'full_name': 'Petro Petrov', 'position': 'developer', 'slack_id': 'V11ED730DDR', 'roles': [1, 2]},
    {'full_name': 'Oleg Olegov', 'position': 'developer', 'slack_id': 'RF4E000Q1CC', 'roles': [1]}
]


@pytest.fixture()
def fill_workers_db(session):
    for role_data in test_role_data:
        new_role = Role(**role_data)
        session.add(new_role)
        session.commit()

    for worker_data in test_workers_data:
        worker_data = deepcopy(worker_data)
        worker_roles_data = worker_data.pop('roles')
        new_worker = Worker(**worker_data)
        session.add(new_worker)
        session.commit()

        worker_roles = [WorkersRolesRelation(new_worker.id, role) for role in worker_roles_data]
        session.add_all(worker_roles)
        session.commit()


def test_get_workers_query_with_empty_db(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_workers()

    assert type(result) is list
    assert len(result) == 0


def test_get_workers_query_with_not_empty_db(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_workers()

    assert type(result) is list
    assert len(result) == len(test_workers_data)


def test_get_worker_by_id_query_with_empty_db(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_worker_by_id(1)

    assert result == 0


def test_get_worker_by_id_query_with_wrong_id(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_worker_by_id('EXEDFFE44E1')

    assert result == 0


def test_get_worker_by_id_query_with_not_empty_db(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result_1 = WorkersQuery.get_worker_by_id(1)
    result_2 = WorkersQuery.get_worker_by_id(2)
    result_3 = WorkersQuery.get_worker_by_id(3)

    assert result_1['id'] == 1
    assert result_1['full_name'] == test_workers_data[0]['full_name']
    assert result_2['id'] == 2
    assert result_2['full_name'] == test_workers_data[1]['full_name']
    assert result_3['id'] == 3
    assert result_3['full_name'] == test_workers_data[2]['full_name']


def test_get_worker_by_slack_id_query_with_empty_db(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_worker_by_slack_id('EXEDFFE44E1')

    assert result == 0


def test_get_worker_by_slack_id_query_with_not_empty_db(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_worker_by_slack_id('EF4ED73Q12X')

    assert result['id'] == 1
    assert result['slack_id'] == 'EF4ED73Q12X'
    assert result['full_name'] == test_workers_data[0]['full_name']


def test_get_worker_by_role_query_with_empty_db(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_workers(role='administrator')

    assert len(result) == 0


def test_get_worker_by_role_query_with_not_empty_db(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.get_workers(role='administrator')

    assert len(result) == 1
    assert result[0]['id'] == 1
    assert result[0]['slack_id'] == 'EF4ED73Q12X'
    assert result[0]['full_name'] == test_workers_data[0]['full_name']


def test_delete_worker_query_with_empty_db(mocker, session):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result = WorkersQuery.delete_worker(1)

    assert result == 0


def test_delete_worker_query_with_not_empty_db(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result_1 = WorkersQuery.delete_worker(1)
    result_2 = WorkersQuery.delete_worker(1)
    result_3 = WorkersQuery.delete_worker(2)

    assert result_1 == 1
    assert result_2 == 0
    assert result_3 == 1


def test_delete_worker_query_with_wrong_id(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)

    result_1 = WorkersQuery.delete_worker(1)
    result_2 = WorkersQuery.delete_worker('two')

    assert result_1 == 1
    assert result_2 == 0


def test_add_new_worker_query_with_roles(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_worker_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'VB4E7G5Q1RR', 'roles': [2]}

    result = WorkersQuery.add_new_worker(new_worker_data)

    assert type(result) == dict
    assert result['id'] == len(test_workers_data) + 1
    assert result['slack_id'] == new_worker_data['slack_id']
    assert result['full_name'] == new_worker_data['full_name']


def test_add_new_worker_query_without_roles(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_worker_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'VB4E7G5Q1RR'}

    result = WorkersQuery.add_new_worker(new_worker_data)

    assert type(result) == dict
    assert result['id'] == len(test_workers_data) + 1
    assert result['slack_id'] == new_worker_data['slack_id']
    assert result['full_name'] == new_worker_data['full_name']


def test_add_new_worker_query_with_wrong_slack_id(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_worker_data = {'full_name': 'Stepan Stepanov', 'position': 'developer', 'slack_id': 'RF4E000Q1CC', 'roles': [1]}

    result = WorkersQuery.add_new_worker(new_worker_data)

    assert result == 0


def test_add_new_worker_query_with_wrong_name(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_worker_data = {'full_name': 'Roman Romanov', 'position': 'developer', 'slack_id': 'RF4E000Q1CC', 'roles': [1]}

    result = WorkersQuery.add_new_worker(new_worker_data)

    assert result == 0


def test_update_worker_query(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'VB4E7G5Q1RR', 'roles': [2]}

    result = WorkersQuery.update_worker(3, new_data)

    assert type(result) == dict
    assert result['id'] == 3
    assert result['slack_id'] == new_data['slack_id']
    assert result['slack_id'] != test_workers_data[2]['slack_id']
    assert result['full_name'] == new_data['full_name']
    assert result['roles'] == ['reviewer']



def test_update_worker_query_with_wrong_id(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'VB4E7G5Q1RR', 'roles': [2]}

    result = WorkersQuery.update_worker(4, new_data)

    assert result == 0


def test_update_worker_query_with_wrong_slack_id(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'V11ED730DDR', 'roles': [2]}

    result = WorkersQuery.update_worker(3, new_data)

    assert result == 0


def test_update_worker_query_with_wrong_slack_id(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'full_name': 'Stepan Stepanov', 'slack_id': 'V11ED730DDR', 'roles': [2]}

    result = WorkersQuery.update_worker(3, new_data)

    assert result == 0


def test_update_worker_query_with_adding_new_role(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'roles': [1, 2]}

    result = WorkersQuery.update_worker(3, new_data)

    assert type(result) == dict
    assert result['id'] == 3
    assert result['roles'] == ['worker', 'reviewer']


def test_update_worker_query_with_deleting_role(mocker, session, fill_workers_db):
    mocker.patch('lambda_workers.orm_services.open_db_session', return_value=session)
    new_data = {'roles': [1]}

    result = WorkersQuery.update_worker(1, new_data)

    assert type(result) == dict
    assert result['id'] == 1
    assert result['roles'] == ['worker']

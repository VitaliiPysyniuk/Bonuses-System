import pytest

from lambda_requests.orm_services import RequestQuery, RequestHistoryQuery
from models.models import Request, RequestHistory

from .test_bonuses_orm_services import fill_bonuses_db
from .test_workers_orm_services import fill_workers_db

test_requests_data = [
    {
        'creator': 2,
        'reviewer': 1,
        'bonus_type': 1,
        'payment_amount': 100,
        'payment_date': '2022-09-14',
        'status': 'created',
        'description': 'New Year bonus'
    },
    {
        'creator': 1,
        'reviewer': 2,
        'bonus_type': 2,
        'payment_amount': 200,
        'payment_date': '2022-09-05',
        'status': 'created',
        'description': 'Newcomer bonus'
    },
    {
        'creator': 3,
        'reviewer': 1,
        'bonus_type': 3,
        'payment_amount': 300,
        'payment_date': '2022-09-14',
        'status': 'created',
        'description': 'Birthday bonus'
    },
]

test_requests_history_data = [
    {
        'request_id': 1,
        'changes': 'created -> approved',
        'editor': 1
    },
    {
        'request_id': 2,
        'changes': 'created -> approved',
        'editor': 2
    },
    {
        'request_id': 1,
        'changes': 'approved -> deleted',
        'editor': 1
    }
]


@pytest.fixture()
def fill_requests_db(session):
    for request_data in test_requests_data:
        new_request = Request(**request_data)
        session.add(new_request)
        session.commit()


@pytest.fixture()
def fill_requests_history_db(session):
    for request_history_data in test_requests_history_data:
        new_request_history = RequestHistory(**request_history_data)
        session.add(new_request_history)
        session.commit()


def test_get_requests_query_with_empty_db(mocker, session):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests()

    assert type(result) is list
    assert len(result) == 0


def test_get_requests_query_with_not_empty_db(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests()

    assert type(result) is list
    assert len(result) == len(test_requests_data)


def test_get_request_by_id_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_request_by_id(request_id=1)
    result_2 = RequestQuery.get_request_by_id(request_id=2)
    result_3 = RequestQuery.get_request_by_id(request_id=3)

    assert type(result_1) is dict
    assert result_1['id'] == 1
    assert type(result_2) is dict
    assert result_2['id'] == 2
    assert type(result_3) is dict
    assert result_3['id'] == 3


def test_get_requests_by_id_query_with_wrong_id(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_request_by_id(request_id=4)

    assert result == 0


def test_get_requests_with_created_status_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests(status='created')

    assert type(result) is list
    assert len(result) == len(test_requests_data)
    assert result[0]['status'] == 'created'
    assert result[-1]['status'] == 'created'


def test_get_requests_with_deleted_status_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests(status='deleted')

    assert type(result) is list
    assert len(result) == 0


def test_get_requests_with_creator_id_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(creator_id=1)
    result_2 = RequestQuery.get_requests(creator_id=2)
    result_3 = RequestQuery.get_requests(creator_id=3)

    assert type(result_1) is list
    assert len(result_1) == 1
    assert type(result_2) is list
    assert len(result_2) == 1
    assert type(result_3) is list
    assert len(result_3) == 1


def test_get_request_with_wrong_creator_id_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests(creator_id=5)

    assert type(result) is list
    assert len(result) == 0


def test_get_requests_with_reviewer_id_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(reviewer_id=1)
    result_2 = RequestQuery.get_requests(reviewer_id=2)
    result_3 = RequestQuery.get_requests(reviewer_id=3)

    assert type(result_1) is list
    assert len(result_1) == 2
    assert type(result_2) is list
    assert len(result_2) == 1
    assert type(result_3) is list
    assert len(result_3) == 0


def test_get_requests_with_wrong_reviewer_id_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests(request_id=5)

    assert type(result) is list
    assert len(result) == 0


def test_get_requests_with_payment_date_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(payment_date='2022-09-14')
    result_2 = RequestQuery.get_requests(payment_date='2022-09-05')
    result_3 = RequestQuery.get_requests(payment_date='2022-09-19')

    assert type(result_1) is list
    assert len(result_1) == 2
    assert type(result_2) is list
    assert len(result_2) == 1
    assert type(result_3) is list
    assert len(result_3) == 0


def test_get_requests_with_payment_date_gt_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(payment_date_gt='2022-09-14')
    result_2 = RequestQuery.get_requests(payment_date_gt='2022-09-04')
    result_3 = RequestQuery.get_requests(payment_date_gt='2022-09-19')

    assert type(result_1) is list
    assert len(result_1) == 0
    assert type(result_2) is list
    assert len(result_2) == 3
    assert type(result_3) is list
    assert len(result_3) == 0


def test_get_requests_with_payment_date_lt_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(payment_date_lt='2022-09-14')
    result_2 = RequestQuery.get_requests(payment_date_lt='2022-09-04')
    result_3 = RequestQuery.get_requests(payment_date_lt='2022-09-19')

    assert type(result_1) is list
    assert len(result_1) == 3
    assert type(result_2) is list
    assert len(result_2) == 0
    assert type(result_3) is list
    assert len(result_3) == 3


def test_get_requests_with_all_params_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.get_requests(status='created', payment_date_lt='2022-09-14', reviewer_id=2)
    result_2 = RequestQuery.get_requests(status='created', payment_date_lt='2022-09-04', reviewer_id=1)
    result_3 = RequestQuery.get_requests(status='deleted', payment_date_lt='2022-09-19', reviewer_id=1)

    assert type(result_1) is list
    assert len(result_1) == 1
    assert type(result_2) is list
    assert len(result_2) == 0
    assert type(result_3) is list
    assert len(result_3) == 0


def test_get_requests_with_wrong_params_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestQuery.get_requests(status='created', payment_date_lt='2022-09-14', reviewer_id='two')

    assert result == 0


def test_add_new_request_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_data = {
        'creator': 2,
        'reviewer': 1,
        'bonus_type': 2,
        'payment_amount': 200,
        'payment_date': '2022-09-10',
        'status': 'created',
        'description': 'Newcomer bonus'
    }

    result = RequestQuery.add_new_request(new_request_data)

    id = result.pop('id')
    result.pop('created_at')

    assert type(result) is dict
    assert id == len(test_requests_data) + 1
    assert result == new_request_data


def test_add_new_request_query_with_wrong_data(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_data = {
        'creator': 6,
        'reviewer': 1,
        'bonus_type': 2,
        'payment_amount': 200,
        'payment_date': '2022-09-10',
        'status': 'created',
        'description': 'Newcomer bonus'
    }

    result = RequestQuery.add_new_request(new_request_data)

    assert result == 0


def test_update_request_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_data = {
        'bonus_type': 3,
        'status': 'approved'
    }

    result = RequestQuery.update_request(1, new_request_data)

    assert type(result) is dict
    assert result['id'] == 1
    assert result['bonus_type'] == 3
    assert result['status'] == 'approved'


def test_update_request_query_with_wrong_data(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_data = {
        'bonus_type': 33,
        'status': 'approved'
    }

    result = RequestQuery.update_request(1, new_request_data)

    assert result == 0


def test_delete_request_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.delete_request(1)
    result_2 = RequestQuery.delete_request(2)
    result_3 = RequestQuery.delete_request(3)

    assert result_1 == 1
    assert result_2 == 1
    assert result_3 == 1


def test_delete_request_query_with_wrong_id(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result_1 = RequestQuery.delete_request(10)
    result_2 = RequestQuery.delete_request('one')

    assert result_1 == 0
    assert result_2 == 0


def test_delete_request_query_when_request_deleted(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_data = {'status': 'deleted'}

    RequestQuery.update_request(1, new_request_data)

    result = RequestQuery.delete_request(1)

    assert result == 0


def test_get_request_history_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db,
                                   fill_requests_history_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestHistoryQuery.get_history(1)

    assert type(result) is list
    assert len(result) == 2
    assert result[0]['request_id'] == 1
    assert result[-1]['request_id'] == 1


def test_get_request_history_query_with_wrong_id(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db,
                                                 fill_requests_history_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)

    result = RequestHistoryQuery.get_history(10)

    assert type(result) is list
    assert len(result) == 0


def test_add_request_history_query(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db,
                                   fill_requests_history_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_history = {
        'request_id': 2,
        'changes': 'approved -> dinned',
        'editor': 1
    }

    result = RequestHistoryQuery.add_history(new_request_history)

    assert type(result) is dict
    assert result['id'] == len(test_requests_data) + 1
    assert result['request_id'] == new_request_history['request_id']
    assert result['editor'] == str(new_request_history['editor'])


def test_add_request_history_query_with_wrong_data(mocker, session, fill_bonuses_db, fill_workers_db, fill_requests_db,
                                                   fill_requests_history_db):
    mocker.patch('lambda_requests.orm_services.open_db_session', return_value=session)
    new_request_history = {
        'request_id': 22,
        'changes': 'approved -> dinned',
        'editor': 1
    }

    result = RequestHistoryQuery.add_history(new_request_history)

    assert result == 0

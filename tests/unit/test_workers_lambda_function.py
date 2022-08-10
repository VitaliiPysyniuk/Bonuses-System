import pytest

from lambda_workers.lambda_function import *


@pytest.fixture
def simple_worker():
    return {'id': 1, 'full_name': 'Oleg Olegov', 'position': 'developer', 'slack_id': 'RF4E000Q1CC', 'roles': ['worker']}


@pytest.fixture()
def workers_event_without_path_params(request):
    event = {
        'resource': '/workers',
        'httpMethod': request.param[0],
        'queryStringParameters': request.param[1]
    }

    return event


@pytest.fixture()
def workers_event_with_path_params(request):
    event = {
        'resource': '/workers/{id}',
        'httpMethod': request.param[0],
        'queryStringParameters': request.param[1],
        'pathParameters': request.param[2]
    }

    return event


def test_get_workers_with_empty_workers_list(mocker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_workers', return_value=[])

    result = get_workers({'queryStringParameters': {}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([])


def test_get_workers_with_not_empty_bonuses_list(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_workers', return_value=[simple_worker])

    result = get_workers({'queryStringParameters': {}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_worker])


def test_get_workers_when_error_occur(mocker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_workers', return_value=0)

    result = get_workers({'queryStringParameters': {}})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_worker_by_id_when_worker_exists(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_worker_by_id', return_value=simple_worker)

    result = get_worker_by_id(1)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_worker)


def test_get_worker_by_id_when_worker_not_exists(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_worker_by_id', return_value=0)

    result = get_worker_by_id(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_worker_by_slack_id_with_correct_slack_id(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_worker_by_slack_id', return_value=simple_worker)

    result = get_workers({'queryStringParameters': {'slack_id': 'RF4E000Q1CC'}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_worker)


def test_get_worker_by_slack_id_with_not_correct_slack_id(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_worker_by_slack_id', return_value=0)

    result = get_workers({'queryStringParameters': {'slack_id': 'RF4E000Q1C1'}})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_worker_by_role(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_workers', return_value=[simple_worker])

    result = get_workers({'queryStringParameters': {'role': 'worker'}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_worker])


def test_create_bonus(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.add_new_worker', return_value=simple_worker)

    result = create_worker({'body': json.dumps(simple_worker)})

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_worker)


def test_create_bonus_when_error_occur(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.add_new_worker', return_value=0)

    result = create_worker({'body': json.dumps(simple_worker)})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_delete_worker(mocker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.delete_worker', return_value=1)

    result = delete_worker(1)

    assert result['statusCode'] == 204
    assert 'body' not in result


def test_delete_worker_when_error_occur(mocker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.delete_worker', return_value=0)

    result = delete_worker(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_update_worker(mocker, simple_worker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.update_worker', return_value=simple_worker)

    result = update_worker(1, {'body': json.dumps({'full_name': 'Oleg'})})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_worker)


def test_update_worker_when_error_occur(mocker):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.update_worker', return_value=0)

    result = update_worker(1, {'body': json.dumps({'full_name': 'Oleg'})})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_lambda_handler_with_wrong_endpoint():
    result = lambda_handler({'resource': '/wrong'}, None)

    assert result['statusCode'] == 404
    assert result['body'] == json.dumps({'message': 'Not found'})


@pytest.mark.parametrize('workers_event_without_path_params', (('GET', {}),), indirect=True)
def test_lambda_handler_get_all_workers(mocker, simple_worker, workers_event_without_path_params):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_workers', return_value=[simple_worker])

    result = lambda_handler(workers_event_without_path_params, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_worker])


@pytest.mark.parametrize('workers_event_without_path_params', (('POST', {}),), indirect=True)
def test_lambda_handler_create_worker(mocker, simple_worker, workers_event_without_path_params):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.add_new_worker', return_value=simple_worker)
    workers_event_without_path_params['body'] = json.dumps(simple_worker)

    result = lambda_handler(workers_event_without_path_params, None)

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_worker)


@pytest.mark.parametrize('workers_event_with_path_params', (('GET', {}, {'id': 1}),), indirect=True)
def test_lambda_handler_get_worker_by_id(mocker, simple_worker, workers_event_with_path_params):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.get_worker_by_id', return_value=simple_worker)

    result = lambda_handler(workers_event_with_path_params, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_worker)


@pytest.mark.parametrize('workers_event_with_path_params', (('PATCH', {}, {'id': 1}),), indirect=True)
def test_lambda_handler_update_worker(mocker, simple_worker, workers_event_with_path_params):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.update_worker', return_value=simple_worker)
    workers_event_with_path_params['body'] = json.dumps(simple_worker)

    result = lambda_handler(workers_event_with_path_params, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_worker)


@pytest.mark.parametrize('workers_event_with_path_params', (('DELETE', {}, {'id': 1}),), indirect=True)
def test_lambda_handler_delete_bonus(mocker, workers_event_with_path_params):
    mocker.patch('lambda_workers.orm_services.WorkersQuery.delete_worker', return_value=1)

    result = lambda_handler(workers_event_with_path_params, None)

    assert result['statusCode'] == 204
    assert 'body' not in result
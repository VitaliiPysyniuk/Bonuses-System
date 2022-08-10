import pytest

from lambda_requests.lambda_function import *


@pytest.fixture
def simple_request():
    return {
        'id': 1,
        'creator': 1,
        'bonus_type': 1,
        'reviewer': 2,
        'payment_amount': 100,
        'payment_date': '2022-09-15',
        'status': 'created',
        'description': 'New request'
    }


@pytest.fixture
def simple_request_history():
    return {
        'id': 1,
        'request_id': 1,
        'editor': 1,
        'changes': 'created -> deleted'
    }


@pytest.fixture()
def requests_event(request):
    event = {
        'resource': request.param[0],
        'httpMethod': request.param[1],
        'queryStringParameters': request.param[2],
        'pathParameters': request.param[3],
        'body': request.param[4]
    }

    return event


def test_get_requests_with_empty_requests_list(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=[])

    result = get_requests({'queryStringParameters': {}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([])


def test_get_requests_with_not_empty_requests_list(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=[simple_request])

    result = get_requests({'queryStringParameters': {}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_request])


def test_get_requests_with_query_params(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=[])

    result = get_requests({'queryStringParameters': {'status': 'delete'}})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([])


def test_get_requests_with_wrong_query_params(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=0, side_effect=KeyError())

    result = get_requests({'queryStringParameters': {'sts': 'delete'}})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_requests_when_error_occur(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=0)

    result = get_requests({'queryStringParameters': {}})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_request_by_id(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_request_by_id', return_value=simple_request)

    result = get_request_by_id(1)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_request)


def test_get_request_by_id_with_wrong_id(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_request_by_id', return_value=0)

    result = get_request_by_id(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_create_request(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.add_new_request', return_value=simple_request)

    result = create_request({'body': json.dumps(simple_request)})

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_request)


def test_create_request_when_error_occur(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.add_new_request', return_value=0)

    result = create_request({'body': json.dumps(simple_request)})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_update_request(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.update_request', return_value=simple_request)

    result = update_request(1, {'body': json.dumps({'status': 'approved'})})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_request)


def test_update_request_when_error_occur(mocker, simple_request):
    mocker.patch('lambda_requests.orm_services.RequestQuery.update_request', return_value=0)

    result = update_request(1, {'body': json.dumps({'status': 'approved'})})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_delete_request(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.delete_request', return_value=1)

    result = delete_request(1)

    assert result['statusCode'] == 204
    assert 'body' not in result


def test_delete_request_when_error_occur(mocker):
    mocker.patch('lambda_requests.orm_services.RequestQuery.delete_request', return_value=0)

    result = delete_request(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_request_history_with_empty_history(mocker):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.get_history', return_value=[])

    result = get_request_history(1)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([])


def test_get_request_history_with_not_empty_history(mocker, simple_request_history):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.get_history',
                 return_value=[simple_request_history])

    result = get_request_history(1)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_request_history])


def test_get_request_history_when_error_occur(mocker):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.get_history', return_value=0)

    result = get_request_history(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_add_request_history(mocker, simple_request_history):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.add_history', return_value=simple_request_history)

    result = add_request_history(1, {'body': json.dumps(simple_request_history)})

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_request_history)


def test_add_request_history_when_error_occur(mocker, simple_request_history):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.add_history', return_value=0)

    result = add_request_history(1, {'body': json.dumps(simple_request_history)})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_lambda_handler_with_wrong_endpoint():
    result = lambda_handler({'resource': '/wrong'}, None)

    assert result['statusCode'] == 404
    assert result['body'] == json.dumps({'message': 'Not found'})


@pytest.mark.parametrize('requests_event', (('/requests', 'GET', {}, {}, {}),), indirect=True)
def test_lambda_handler_get_all_requests(mocker, simple_request, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_requests', return_value=[simple_request])

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_request])


@pytest.mark.parametrize('requests_event', (('/requests', 'POST', {}, {}, {}),), indirect=True)
def test_lambda_handler_create_requests(mocker, simple_request, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestQuery.add_new_request', return_value=simple_request)
    requests_event['body'] = json.dumps(simple_request)

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_request)


@pytest.mark.parametrize('requests_event', (('/requests/{id}', 'GET', {}, {'id': 1}, {}),), indirect=True)
def test_lambda_handler_get_request_by_id(mocker, simple_request, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestQuery.get_request_by_id', return_value=simple_request)

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_request)


@pytest.mark.parametrize('requests_event', (('/requests/{id}', 'PATCH', {}, {'id': 1}, {}),), indirect=True)
def test_lambda_handler_update_request(mocker, simple_request, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestQuery.update_request', return_value=simple_request)
    requests_event['body'] = json.dumps({'status': 'created'})

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_request)


@pytest.mark.parametrize('requests_event', (('/requests/{id}', 'DELETE', {}, {'id': 1}, {}),), indirect=True)
def test_lambda_handler_delete_request(mocker, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestQuery.delete_request', return_value=1)

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 204
    assert 'body' not in result


@pytest.mark.parametrize('requests_event', (('/requests/{id}/history', 'GET', {}, {'id': 1}, {}),), indirect=True)
def test_lambda_handler_get_request_history(mocker, simple_request_history, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.get_history', return_value=[simple_request_history])

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_request_history])


@pytest.mark.parametrize('requests_event', (('/requests/{id}/history', 'POST', {}, {'id': 1}, {}),), indirect=True)
def test_lambda_handler_add_request_history(mocker, simple_request_history, requests_event):
    mocker.patch('lambda_requests.orm_services.RequestHistoryQuery.add_history', return_value=simple_request_history)
    requests_event['body'] = json.dumps(simple_request_history)

    result = lambda_handler(requests_event, None)

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_request_history)

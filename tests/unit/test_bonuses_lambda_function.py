import pytest

from lambda_bonuses.lambda_function import *


@pytest.fixture
def simple_bonus():
    return {'id': 1, 'type': 'Overtime', 'description': 'Overtime'}


@pytest.fixture
def bonuses_event(request):
    event = {
        'resource': request.param[0],
        'httpMethod': request.param[1],
        'pathParameters': request.param[2]
    }

    return event


def test_get_bonuses_with_empty_bonuses_list(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonuses', return_value=[])

    result = get_bonuses()

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([])


def test_get_bonuses_with_not_empty_bonuses_list(mocker, simple_bonus):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonuses',
                 return_value=[simple_bonus])

    result = get_bonuses()

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_bonus])


def test_get_bonuses_when_error_occur(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonuses', return_value=0)

    result = get_bonuses()

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_get_bonus_by_id_when_bonus_exists(mocker, simple_bonus):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonus_by_id',
                 return_value=simple_bonus)

    result = get_bonus_by_id(1)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_bonus)


def test_get_bonus_by_id_when_bonus_not_exists(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonus_by_id', return_value=0)

    result = get_bonus_by_id(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_create_bonus(mocker, simple_bonus):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.add_new_bonus', return_value=simple_bonus)

    result = create_bonus({'body': json.dumps(simple_bonus)})

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_bonus)


def test_create_bonus_when_error_occur(mocker, simple_bonus):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.add_new_bonus', return_value=0)

    result = create_bonus({'body': json.dumps(simple_bonus)})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_update_bonus(mocker, simple_bonus):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.update_bonus', return_value=simple_bonus)

    result = update_bonus(1, {'body': json.dumps({'type': 'Overtime'})})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_bonus)


def test_update_bonus_when_error_occur(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.update_bonus', return_value=0)

    result = update_bonus(1, {'body': json.dumps({'type': 'Overtime'})})

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_delete_bonus(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.delete_bonus', return_value=1)

    result = delete_bonus(1)

    assert result['statusCode'] == 204
    assert 'body' not in result


def test_delete_bonus_when_error_occur(mocker):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.delete_bonus', return_value=0)

    result = delete_bonus(1)

    assert result['statusCode'] == 400
    assert result['body'] == json.dumps({'message': 'Bad Request'})


def test_lambda_handler_with_wrong_endpoint():
    result = lambda_handler({'resource': '/wrong'}, None)

    assert result['statusCode'] == 404
    assert result['body'] == json.dumps({'message': 'Not found'})


@pytest.mark.parametrize('bonuses_event', (('/bonuses', 'GET', {}),), indirect=True)
def test_lambda_handler_get_all_bonuses(mocker, simple_bonus, bonuses_event):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonuses',
                 return_value=[simple_bonus])

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps([simple_bonus])


@pytest.mark.parametrize('bonuses_event', (('/bonuses', 'POST', {}),), indirect=True)
def test_lambda_handler_create_bonus(mocker, simple_bonus, bonuses_event):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.add_new_bonus', return_value=simple_bonus)
    bonuses_event['body'] = json.dumps(simple_bonus)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps(simple_bonus)


@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'GET', {'id': 1}),), indirect=True)
def test_lambda_handler_get_bonus_by_id(mocker, simple_bonus, bonuses_event):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.get_bonus_by_id', return_value=simple_bonus)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_bonus)


@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'PATCH', {'id': 1}),), indirect=True)
def test_lambda_handler_update_bonus(mocker, simple_bonus, bonuses_event):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.update_bonus', return_value=simple_bonus)
    bonuses_event['body'] = json.dumps(simple_bonus)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(simple_bonus)


@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'DELETE', {'id': 1}),), indirect=True)
def test_lambda_handler_delete_bonus(mocker, simple_bonus, bonuses_event):
    mocker.patch('lambda_bonuses.lambda_function.BonusesQuery.delete_bonus', return_value=1)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 204
    assert 'body' not in result

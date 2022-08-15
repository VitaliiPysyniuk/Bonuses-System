import pytest
import os
from unittest import mock
# from dotenv import load_dotenv
import json
from copy import deepcopy

from ..unit.test_bonuses_orm_services import test_bonuses_data
from ..unit.test_bonuses_lambda_function import bonuses_event
from lambda_bonuses.lambda_function import lambda_handler

test_bonuses_data_with_id = list(map(lambda item: {'id': item[0] + 1, **item[1]}, enumerate(test_bonuses_data)))

# load_dotenv('.env.test')

TEST_ENV_VARIABLES = {
    'POSTGRES_USER': os.environ.get('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
    'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
    'POSTGRES_PORT': os.environ.get('POSTGRES_PORT'),
    'POSTGRES_DB': os.environ.get('POSTGRES_DB')
}


@pytest.fixture(scope='module')
def mock_settings_env_vars(clear_db):
    mock.patch.dict(os.environ, TEST_ENV_VARIABLES)


@pytest.mark.parametrize('bonuses_event', (('/bonuse', 'GET', {}),), indirect=True)
def test_lambda_handler_with_wrong_endpoint(bonuses_event):
    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 404
    assert result['body'] == json.dumps({'message': 'Not found'})


@pytest.mark.parametrize('bonus', deepcopy(test_bonuses_data_with_id))
@pytest.mark.parametrize('bonuses_event', (('/bonuses', 'POST', {}),), indirect=True)
def test_lambda_handler_post_request(bonus, bonuses_event):
    expected_id = bonus.pop('id')
    bonuses_event['body'] = json.dumps(bonus)

    result = lambda_handler(bonuses_event, None)
    body = json.loads(result['body'])
    id = body.pop('id')

    assert result['statusCode'] == 201
    assert id == expected_id
    assert body == bonus


@pytest.mark.parametrize('bonuses_event', (('/bonuses', 'POST', {}),), indirect=True)
def test_lambda_handler_post_request_with_wrong_data(bonuses_event):
    new_bonus = {'type': 'New Year', 'description': 'New Year bonus'}
    bonuses_event['body'] = json.dumps(new_bonus)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400


@pytest.mark.parametrize('bonuses_event', (('/bonuses', 'GET', {}),), indirect=True)
def test_lambda_handler_get_request(bonuses_event):
    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(test_bonuses_data_with_id)


@pytest.mark.parametrize('bonus_index', [0, 1, 2, 3])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'GET', {}),), indirect=True)
def test_lambda_handler_get_by_id_request(bonus_index, bonuses_event):
    bonuses_event['pathParameters'] = {'id': bonus_index + 1}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps(test_bonuses_data_with_id[bonus_index])


@pytest.mark.parametrize('bonus_index', [4, 5, 6, 7])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'GET', {}),), indirect=True)
def test_lambda_handler_get_by_id_request_with_wrong_id(bonus_index, bonuses_event):
    bonuses_event['pathParameters'] = {'id': bonus_index + 1}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400


@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'GET', {}),), indirect=True)
def test_lambda_handler_get_by_id_request_with_incorrect_id(bonuses_event):
    bonuses_event['pathParameters'] = {'id':  'one'}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400


@pytest.mark.parametrize('existing_bonus,new_data',
                         [(test_bonuses_data_with_id[0], {'type': 'new_year'}),
                          (test_bonuses_data_with_id[1], {'description': 'newcomer_b'}),
                          (test_bonuses_data_with_id[2], {'type': 'b-day'}),
                          (test_bonuses_data_with_id[3], {'type': 'annual', 'description': 'company b-day'})])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'PATCH', {}),), indirect=True)
def test_lambda_handler_patch_request(existing_bonus, new_data, bonuses_event):
    bonuses_event['pathParameters'] = {'id': existing_bonus['id']}
    bonuses_event['body'] = json.dumps(new_data)

    result = lambda_handler(bonuses_event, None)
    body = json.loads(result['body'])

    assert result['statusCode'] == 200
    for key in new_data.keys():
        assert body[key] == new_data[key]


@pytest.mark.parametrize('existing_bonus,new_data',
                         [({'id': 59}, {'type': 'new_year'}),
                          (test_bonuses_data_with_id[1], {'type': 'new_year'})])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'PATCH', {}),), indirect=True)
def test_lambda_handler_patch_request_with_wrong_data(existing_bonus, new_data, bonuses_event):
    bonuses_event['pathParameters'] = {'id': existing_bonus['id']}
    bonuses_event['body'] = json.dumps(new_data)

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400


@pytest.mark.parametrize('bonus_index', [0, 1, 2, 3])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'DELETE', {}),), indirect=True)
def test_lambda_handler_delete_request(bonus_index, bonuses_event):
    bonuses_event['pathParameters'] = {'id': bonus_index + 1}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 204


@pytest.mark.parametrize('bonus_index', [4, 5, 6, 7])
@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'DELETE', {}),), indirect=True)
def test_lambda_handler_delete_request_with_wrong_id(bonus_index, bonuses_event):
    bonuses_event['pathParameters'] = {'id': bonus_index + 1}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400


@pytest.mark.parametrize('bonuses_event', (('/bonuses/{id}', 'DELETE', {}),), indirect=True)
def test_lambda_handler_delete_request_with_incorrect_id(bonuses_event):
    bonuses_event['pathParameters'] = {'id':  'one'}

    result = lambda_handler(bonuses_event, None)

    assert result['statusCode'] == 400
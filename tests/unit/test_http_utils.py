import json

from utils.http import http_ok, http_created


def test_http_ok():
    result = http_ok({})

    assert result['statusCode'] == 200
    assert result['body'] == json.dumps({})
    assert result['headers']['Content-Type'] == 'application/json'


def test_http_created():
    result = http_created({})

    assert result['statusCode'] == 201
    assert result['body'] == json.dumps({})
    assert result['headers']['Content-Type'] == 'application/json'
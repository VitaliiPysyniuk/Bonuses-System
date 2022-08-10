from .orm_services import RequestQuery, RequestHistoryQuery
from utils.http import *


def get_requests(event):
    query_params = event['queryStringParameters']

    if not query_params:
        requests = RequestQuery.get_requests()
    else:
        try:
            requests = RequestQuery.get_requests(**query_params)
        except KeyError:
            return HTTP_BAD_REQUEST

    if type(requests) is list:
        return http_ok(requests)

    return HTTP_BAD_REQUEST


def get_request_by_id(id):
    request = RequestQuery.get_request_by_id(request_id=id)

    if request:
        return http_ok(request)

    return HTTP_BAD_REQUEST


def create_request(event):
    data = json.loads(event['body'])
    data['status'] = 'created'

    created_request = RequestQuery.add_new_request(data)

    if created_request:
        return http_created(created_request)

    return HTTP_BAD_REQUEST


def update_request(id, event):
    data = json.loads(event['body'])

    updated_request = RequestQuery.update_request(id, data)

    if updated_request:
        return http_ok(updated_request)

    return HTTP_BAD_REQUEST


def delete_request(id):
    deleted = RequestQuery.delete_request(int(id))

    if deleted:
        return HTTP_NO_CONTENT

    return HTTP_BAD_REQUEST


def get_request_history(id):
    history = RequestHistoryQuery.get_history(id)

    if type(history) is list:
        return http_ok(history)

    return HTTP_BAD_REQUEST


def add_request_history(id, event):
    data = json.loads(event['body'])
    data['request_id'] = id

    created_history = RequestHistoryQuery.add_history(data)

    if created_history:
        return http_created(created_history)

    return HTTP_BAD_REQUEST


def lambda_handler(event, context):
    if event['resource'] == '/requests':
        if event['httpMethod'] == 'GET':
            http_response = get_requests(event)

        elif event['httpMethod'] == 'POST':
            http_response = create_request(event)

    elif event['resource'] == '/requests/{id}':
        request_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            http_response = get_request_by_id(request_id)

        elif event['httpMethod'] == 'PATCH':
            http_response = update_request(request_id, event)

        elif event['httpMethod'] == 'DELETE':
            http_response = delete_request(request_id)

    elif event['resource'] == '/requests/{id}/history':
        request_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            http_response = get_request_history(request_id)

        elif event['httpMethod'] == 'POST':
            http_response = add_request_history(request_id, event)

    else:
        http_response = HTTP_NOT_FOUND

    return http_response

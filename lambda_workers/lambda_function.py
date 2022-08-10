from .orm_services import WorkersQuery
from utils.http import *


def get_workers(event):
    query_params = event['queryStringParameters']
    if query_params and 'slack_id' in query_params:
        slack_id = query_params.get('slack_id')
        worker = WorkersQuery.get_worker_by_slack_id(slack_id)

        if worker:
            return http_ok(worker)

    elif query_params and 'role' in query_params:
        role = query_params.get('role')
        workers = WorkersQuery.get_workers(role=role)

        if type(workers) is list:
            return http_ok(workers)

    else:
        workers = WorkersQuery.get_workers()
        if type(workers) is list:
            return http_ok(workers)

    return HTTP_BAD_REQUEST


def get_worker_by_id(id):
    worker = WorkersQuery.get_worker_by_id(id)

    if worker:
        return http_ok(worker)

    return HTTP_BAD_REQUEST


def create_worker(event):
    data = json.loads(event['body'])

    created_worker = WorkersQuery.add_new_worker(data)

    if created_worker:
        return http_created(created_worker)

    return HTTP_BAD_REQUEST


def update_worker(id, event):
    data = json.loads(event['body'])

    updated_worker = WorkersQuery.update_worker(id, data)

    if updated_worker:
        return http_ok(updated_worker)

    return HTTP_BAD_REQUEST


def delete_worker(id):
    deleted = WorkersQuery.delete_worker(id)

    if deleted:
        return HTTP_NO_CONTENT

    return HTTP_BAD_REQUEST


def lambda_handler(event, context):
    if event['resource'] == '/workers':
        if event['httpMethod'] == 'GET':
            http_response = get_workers(event)

        elif event['httpMethod'] == 'POST':
            http_response = create_worker(event)

    elif event['resource'] == '/workers/{id}':
        worker_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            http_response = get_worker_by_id(worker_id)

        elif event['httpMethod'] == 'PATCH':
            http_response = update_worker(worker_id, event)

        elif event['httpMethod'] == 'DELETE':
            http_response = delete_worker(worker_id)

    else:
        http_response = HTTP_NOT_FOUND

    return http_response

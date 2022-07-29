import json

from orm_services import UsersQuery

HTTP_BAD_REQUEST = {
    'statusCode': 400,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'message': 'Bad Request'})
}


def http_ok(data):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data)
    }


def get_workers(event):
    query_params = event['queryStringParameters']
    if query_params and 'slack_id' in query_params:
        slack_id = query_params.get('slack_id')
        worker = UsersQuery.get_user_by_slack_id(slack_id)

        if worker:
            return http_ok(worker)

    if query_params and 'role' in query_params:
        role = query_params.get('role')
        worker = UsersQuery.get_users(role=role)

        if worker:
            return http_ok(worker)

    else:
        workers = UsersQuery.get_users()
        if workers:
            return http_ok(workers)

    return HTTP_BAD_REQUEST


def get_worker_by_id(id):
    worker = UsersQuery.get_user_by_id(id)

    if worker:
        response = http_ok(worker)

    else:
        response = HTTP_BAD_REQUEST

    return response


def create_worker(event):
    data = json.loads(event['body'])

    created_worker = UsersQuery.add_new_user(data)

    if created_worker:
        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(created_worker)
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def update_worker(id, event):
    data = json.loads(event['body'])

    updated_worker = UsersQuery.update_user(id, data)

    if updated_worker:
        response = http_ok(updated_worker)

    else:
        response = HTTP_BAD_REQUEST

    return response


def delete_worker(id):
    deleted = UsersQuery.delete_user(id)

    if deleted:
        response = {
            'statusCode': 204,
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def lambda_handler(event, context):
    print('INFO: start')
    print(event)
    if event['resource'] == '/workers':
        if event['httpMethod'] == 'GET':
            result = get_workers(event)

        elif event['httpMethod'] == 'POST':
            result = create_worker(event)

    elif event['resource'] == '/workers/{id}':
        worker_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            result = get_worker_by_id(worker_id)

        elif event['httpMethod'] == 'PATCH':
            result = update_worker(worker_id, event)

        elif event['httpMethod'] == 'DELETE':
            result = delete_worker(worker_id)

    else:
        result = {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Not found'})
        }

    print('INFO: end')
    print(result)
    return result

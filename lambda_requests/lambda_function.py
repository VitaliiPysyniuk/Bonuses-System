import json

from orm_services import RequestQuery, RequestHistoryQuery, RequestPayQuery

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


def get_requests(event):
    query_params = event['queryStringParameters']
    requests = None

    if not query_params:
        requests = RequestQuery.get_requests()
    else:
        try:
            if int(query_params['type']) == 1:
                requests = RequestQuery.get_filtered_requests(
                    status=query_params['status'],
                    reviewer_id=int(query_params['reviewer_id'])
                )

            elif int(query_params['type']) == 2:
                requests = RequestQuery.get_worker_pending_unpaid_requests(creator_id=int(query_params['creator_id']))

            elif int(query_params['type']) == 3:
                requests = RequestQuery.get_worker_approved_denied_requests(creator_id=int(query_params['creator_id']))

            elif int(query_params['type']) == 4:
                requests = RequestQuery.get_worker_deleted_requests(creator_id=int(query_params['creator_id']))

            elif int(query_params['type']) == 5:
                requests = RequestQuery.get_administrator_all_requests(query_name=query_params['query_name'])

            elif int(query_params['type']) == 6:
                requests = RequestPayQuery.get_requests_by_payment_date()

        except KeyError:
            return HTTP_BAD_REQUEST

    if requests or len(requests) == 0:
        response = http_ok(requests)

    else:
        response = HTTP_BAD_REQUEST

    return response


def get_request_by_id(id):
    request = RequestQuery.get_requests(id)

    if request:
        response = http_ok(request)

    else:
        response = HTTP_BAD_REQUEST

    return response


def create_request(event):
    data = json.loads(event['body'])
    data['status'] = 'created'

    created_request = RequestQuery.add_new_request(data)

    if created_request:
        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(created_request)
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def update_request(id, event):
    data = json.loads(event['body'])

    updated_request = RequestQuery.update_request(id, data)

    if updated_request:
        response = http_ok(updated_request)

    else:
        response = HTTP_BAD_REQUEST

    return response


def delete_request(id):
    deleted = RequestQuery.delete_request(int(id))

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


def get_request_history(id):
    history = RequestHistoryQuery.get_request_history(id)

    if history:
        response = http_ok(history)

    else:
        response = HTTP_BAD_REQUEST

    return response


def add_request_history(id, event):
    data = json.loads(event['body'])
    data['request_id'] = id

    created_history = RequestHistoryQuery.add_history(data)

    if created_history:
        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(created_history)
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def lambda_handler(event, context):
    print('INFO: start')
    print(event)
    if event['resource'] == '/requests':
        if event['httpMethod'] == 'GET':
            result = get_requests(event)

        elif event['httpMethod'] == 'POST':
            result = create_request(event)

    elif event['resource'] == '/requests/{id}':
        request_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            result = get_request_by_id(request_id)

        elif event['httpMethod'] == 'PATCH':
            result = update_request(request_id, event)

        elif event['httpMethod'] == 'DELETE':
            result = delete_request(request_id)

    elif event['resource'] == '/requests/{id}/history':
        request_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            result = get_request_history(request_id)

        elif event['httpMethod'] == 'POST':
            result = add_request_history(request_id, event)

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

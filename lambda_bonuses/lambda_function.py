import json

from orm_services import BonusesQuery

HTTP_BAD_REQUEST = {
    'statusCode': 400,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'message': 'Bad Request'})
}


def get_bonuses():
    bonuses = BonusesQuery.get_bonuses()

    if bonuses:
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(bonuses)
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def create_bonus(event):
    data = json.loads(event['body'])

    created_bonus = BonusesQuery.add_new_bonus(data)

    if created_bonus:
        response = {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(created_bonus)
        }
    else:
        response = HTTP_BAD_REQUEST

    return response


def update_bonus(id, event):
    data = json.loads(event['body'])

    updated_bonus = BonusesQuery.update_bonuses(id, data)

    if updated_bonus:
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(updated_bonus)
        }

    else:
        response = HTTP_BAD_REQUEST

    return response


def delete_bonus(id):
    deleted = BonusesQuery.delete_bonuses(id)

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
    if event['resource'] == '/bonuses':
        if event['httpMethod'] == 'GET':
            result = get_bonuses()

        elif event['httpMethod'] == 'POST':
            result = create_bonus(event)

    elif event['resource'] == '/bonuses/{id}':
        bonus_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'PATCH':
            result = update_bonus(bonus_id, event)

        elif event['httpMethod'] == 'DELETE':
            result = delete_bonus(bonus_id)

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

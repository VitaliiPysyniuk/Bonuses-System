from orm_services import BonusesQuery
from utils.http import *


def get_bonuses():
    bonuses = BonusesQuery.get_bonuses()

    if bonuses:
        response = http_ok(bonuses)

    else:
        response = HTTP_BAD_REQUEST

    return response


def get_bonus_by_id(bonus_id):
    bonus = BonusesQuery.get_bonus_by_id(bonus_id)

    if bonus:
        response = http_ok(bonus)

    else:
        response = HTTP_BAD_REQUEST

    return response


def create_bonus(event):
    data = json.loads(event['body'])

    created_bonus = BonusesQuery.add_new_bonus(data)

    if created_bonus:
        response = http_created(created_bonus)

    else:
        response = HTTP_BAD_REQUEST

    return response


def update_bonus(id, event):
    data = json.loads(event['body'])

    updated_bonus = BonusesQuery.update_bonuses(id, data)

    if updated_bonus:
        response = http_ok(updated_bonus)

    else:
        response = HTTP_BAD_REQUEST

    return response


def delete_bonus(id):
    deleted = BonusesQuery.delete_bonuses(id)

    if deleted:
        response = HTTP_NO_CONTENT

    else:
        response = HTTP_BAD_REQUEST

    return response


def lambda_handler(event, context):
    if event['resource'] == '/bonuses':
        if event['httpMethod'] == 'GET':
            http_response = get_bonuses()

        elif event['httpMethod'] == 'POST':
            http_response = create_bonus(event)

    elif event['resource'] == '/bonuses/{id}':
        bonus_id = event['pathParameters'].get('id')

        if event['httpMethod'] == 'GET':
            http_response = get_bonus_by_id(bonus_id)

        elif event['httpMethod'] == 'PATCH':
            http_response = update_bonus(bonus_id, event)

        elif event['httpMethod'] == 'DELETE':
            http_response = delete_bonus(bonus_id)

    else:
        http_response = HTTP_NOT_FOUND

    return http_response

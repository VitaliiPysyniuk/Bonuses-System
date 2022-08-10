from .orm_services import BonusesQuery
from utils.http import *


def get_bonuses():
    bonuses = BonusesQuery.get_bonuses()

    if type(bonuses) is list:
        return http_ok(bonuses)

    return HTTP_BAD_REQUEST


def get_bonus_by_id(bonus_id):
    bonus = BonusesQuery.get_bonus_by_id(bonus_id)

    if bonus:
        return http_ok(bonus)

    return HTTP_BAD_REQUEST


def create_bonus(event):
    data = json.loads(event['body'])

    created_bonus = BonusesQuery.add_new_bonus(data)

    if created_bonus:
        return http_created(created_bonus)

    return HTTP_BAD_REQUEST


def update_bonus(id, event):
    data = json.loads(event['body'])

    updated_bonus = BonusesQuery.update_bonus(id, data)

    if updated_bonus:
        return http_ok(updated_bonus)

    return HTTP_BAD_REQUEST


def delete_bonus(id):
    deleted = BonusesQuery.delete_bonus(id)

    if deleted:
        return HTTP_NO_CONTENT

    return HTTP_BAD_REQUEST


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
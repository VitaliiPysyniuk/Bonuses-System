import json

from orm_services import BonusesQuery

from aws_lambda_powertools.event_handler import APIGatewayRestResolver

app = APIGatewayRestResolver()


@app.get('/bonuses')
def get_bonuses():
    bonuses = BonusesQuery.get_bonuses()
    return bonuses


@app.post('/bonuses')
def create_bonus():
    data = json.loads(app.current_event.body)

    created_bonus = BonusesQuery.add_new_bonus(data)

    if created_bonus:
        return created_bonus
    else:
        return {'error': 'Something went wrong'}


@app.patch('/bonuses/<id>')
def update_bonus(id):
    data = json.loads(app.current_event.body)

    updated_bonus = BonusesQuery.update_bonuses(id, data)

    if updated_bonus:
        return updated_bonus
    else:
        return {'error': 'Something went wrong'}


@app.delete('/bonuses/<id>')
def delete_bonus(id):
    deleted = BonusesQuery.delete_bonuses(int(id))

    return {'deleted': bool(deleted)}


def lambda_handler(event, context):
    return app.resolve(event, context)

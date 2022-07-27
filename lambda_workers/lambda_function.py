import json
from orm_services import UsersQuery

from aws_lambda_powertools.event_handler import APIGatewayRestResolver

app = APIGatewayRestResolver()


@app.get('/workers')
def get_workers():
    workers = UsersQuery.get_users()
    return workers


@app.get('/workers/<id>')
def get_worker_by_id(id):
    worker = UsersQuery.get_user_by_id(id)
    return worker


@app.post('/workers')
def create_worker():
    data = json.loads(app.current_event.body)

    created_worker = UsersQuery.add_new_user(data)

    if created_worker:
        return created_worker
    else:
        return {'error': 'Something went wrong'}


@app.patch('/workers/<id>')
def update_worker(id):
    data = json.loads(app.current_event.body)

    updated_worker = UsersQuery.update_user(id, data)

    if updated_worker:
        return updated_worker
    else:
        return {'error': 'Something went wrong'}


@app.delete('/workers/<id>')
def delete_worker(id):
    deleted = UsersQuery.delete_user(int(id))

    return {'deleted': bool(deleted)}


def lambda_handler(event, context):
    return app.resolve(event, context)

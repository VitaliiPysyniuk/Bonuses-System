from sqlalchemy.exc import SQLAlchemyError

from models.models import Worker, WorkersRolesRelation, Role
from utils.database import open_db_session


class WorkersQuery:
    @staticmethod
    def get_workers(worker_id=None, slack_id=None, role=None):
        with open_db_session() as session:
            try:
                query = session.query(Worker, WorkersRolesRelation.role_id, Role.role_name)

                if worker_id is not None:
                    query = query.filter(Worker.id == worker_id)
                if slack_id is not None:
                    query = query.filter(Worker.slack_id == slack_id)
                if role is not None:
                    query = query.filter(Role.role_name == role)

                query = query.join(WorkersRolesRelation, Worker.id == WorkersRolesRelation.worker_id) \
                    .join(Role, WorkersRolesRelation.role_id == Role.id)

                query_result = query.all()

            except SQLAlchemyError as error:
                print(error)
                return 0

        return WorkersQuery._parse_workers(query_result)

    @staticmethod
    def get_worker_by_id(worker_id):
        query_result = WorkersQuery.get_workers(worker_id=worker_id)

        if query_result and len(query_result) == 1:
            worker = query_result[0]
            return worker

        return 0

    @staticmethod
    def get_worker_by_slack_id(slack_id):
        query_result = WorkersQuery.get_workers(slack_id=slack_id)

        if query_result and len(query_result) == 1:
            worker = query_result[0]
            return worker

        return 0

    @staticmethod
    def _parse_workers(workers_data):
        parsed_result = {}

        for item in workers_data:
            if item['Worker'].id not in parsed_result:
                parsed_result[item['Worker'].id] = {
                    'id': item['Worker'].id,
                    'full_name': item['Worker'].full_name,
                    'position': item['Worker'].position,
                    'slack_id': item['Worker'].slack_id,
                    'roles': [item['role_name']]
                }
            else:
                parsed_result[item['Worker'].id]['roles'].append(item['role_name'])

        return list(parsed_result.values())

    @staticmethod
    def update_worker(worker_id, data):
        with open_db_session() as session:
            try:
                worker = WorkersQuery.get_worker_by_id(worker_id)
                if not worker:
                    return 0

                roles_data = data.pop('roles', None)

                if roles_data is not None and roles_data != worker['roles']:
                    worker_roles = session.query(WorkersRolesRelation)\
                        .filter(WorkersRolesRelation.worker_id == worker_id).all()

                    for worker_role in worker_roles:
                        if worker_role.role_id not in roles_data:
                            session.query(WorkersRolesRelation)\
                                .filter(WorkersRolesRelation.id == worker_role.id).delete()
                        else:
                            roles_data.remove(worker_role.role_id)

                    if len(roles_data) > 0:
                        new_roles = [WorkersRolesRelation(worker['id'], role) for role in roles_data]
                        session.add_all(new_roles)

                worker_to_update = session.query(Worker).filter(Worker.id == worker_id).first()

                for key, value in data.items():
                    worker_to_update.__setattr__(key, value)

                session.commit()
                session.flush()
                updated_worker = WorkersQuery.get_worker_by_id(worker_id)

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return updated_worker

    @staticmethod
    def delete_worker(worker_id):
        with open_db_session() as session:
            try:
                query = session.query(Worker).filter(Worker.id == worker_id)
                query_result = query.delete()

                session.commit()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return query_result

    @staticmethod
    def add_new_worker(data):
        with open_db_session() as session:
            try:
                roles_data = data.pop('roles', None)

                new_worker = Worker(**data)
                session.add(new_worker)
                session.flush()

                if roles_data is not None:
                    new_roles = [WorkersRolesRelation(new_worker.id, role) for role in roles_data]
                    session.add_all(new_roles)
                else:
                    new_role = WorkersRolesRelation(new_worker.id, 1)
                    session.add(new_role)

                session.commit()
                created_worker = new_worker.to_dict()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return created_worker

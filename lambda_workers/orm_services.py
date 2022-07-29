import sqlalchemy as db
from sqlalchemy.orm.session import Session
from models import User, UsersRolesRelation, Roles
import os

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

engine = db.create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')


class UsersQuery:
    @staticmethod
    def get_users(user_id=None, slack_id=None, role=None):
        with Session(engine) as session:
            try:
                query = session.query(User, UsersRolesRelation.role_id, Roles.role_name)

                if user_id is not None:
                    query = query.filter(User.id == user_id)
                if slack_id is not None:
                    query = query.filter(User.slack_id == slack_id)

                query = query.join(UsersRolesRelation, User.id == UsersRolesRelation.user_id) \
                    .join(Roles, UsersRolesRelation.role_id == Roles.id)

                if role:
                    query = query.filter(Roles.role_name == role)
                    print(query)

                query_result = query.all()
            except Exception as e:
                return None

        return UsersQuery._parse_users(query_result)

    @staticmethod
    def get_user_by_id(user_id):
        user = UsersQuery.get_users(user_id=user_id)[0]

        return user

    @staticmethod
    def get_user_by_slack_id(slack_id):
        user = UsersQuery.get_users(slack_id=slack_id)[0]

        return user

    @staticmethod
    def _parse_users(users_data):
        parsed_result = {}

        for item in users_data:
            if item['User'].id not in parsed_result:
                parsed_result[item['User'].id] = {
                    'id': item['User'].id,
                    'full_name': item['User'].full_name,
                    'position': item['User'].position,
                    'slack_id': item['User'].slack_id,
                    'roles': [item['role_name']]
                }
            else:
                parsed_result[item['User'].id]['roles'].append(item['role_name'])

        return list(parsed_result.values())

    @staticmethod
    def update_user(user_id, data):
        with Session(engine) as session:
            try:
                user = UsersQuery.get_user_by_id(user_id)
                roles_data = data.pop('roles', None)

                if roles_data is not None and roles_data != user['roles']:
                    user_roles = session.query(UsersRolesRelation).filter(UsersRolesRelation.user_id == user_id).all()

                    for user_role in user_roles:
                        if user_role.role_id not in roles_data:
                            session.query(UsersRolesRelation).filter(UsersRolesRelation.id == user_role.id).delete()
                        else:
                            roles_data.remove(user_role.role_id)

                    if len(roles_data) > 0:
                        new_roles = [UsersRolesRelation(user['id'], role) for role in roles_data]
                        session.add_all(new_roles)

                user_to_update = session.query(User).filter(User.id == user_id).first()

                for key, value in data.items():
                    user_to_update.__setattr__(key, value)

                session.commit()
                session.flush()
                updated_user = user_to_update.to_dict()
            except Exception as e:
                session.rollback()
                return 0

        return updated_user

    @staticmethod
    def delete_user(user_id):
        with Session(engine) as session:
            try:
                query = session.query(User).filter(User.id == user_id)
                query.delete()

                session.commit()
            except Exception as e:
                session.rollback()
                return 0

        return 1

    @staticmethod
    def add_new_user(data):
        with Session(engine) as session:
            try:
                roles_data = data.pop('roles', None)

                new_user = User(**data)
                session.add(new_user)
                session.flush()

                if data is not None:
                    new_roles = [UsersRolesRelation(new_user.id, role) for role in roles_data]
                    session.add_all(new_roles)

                session.commit()
                created_user = new_user.to_dict()
            except Exception as e:
                session.rollback()
                return 0

        return created_user

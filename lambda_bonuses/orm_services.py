import sqlalchemy as db
from sqlalchemy.orm.session import Session
import os

from models import Bonus

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

engine = db.create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')


class BonusesQuery:

    @staticmethod
    def get_bonuses(bonus_id=None):
        with Session(engine) as session:
            try:
                query = session.query(Bonus).order_by(Bonus.id)

                if bonus_id is not None:
                    query = query.filter(Bonus.id == bonus_id)
                    query_result = query.first()

                    return query_result

                query_result = query.all()
                query_result = [bonus.to_dict() for bonus in query_result]
            except Exception as e:
                return None

        return query_result

    @staticmethod
    def get_bonus_by_id(bonus_id):
        bonus = BonusesQuery.get_bonuses(bonus_id)
        bonus = bonus.to_dict()

        return bonus

    @staticmethod
    def update_bonuses(bonus_id, data):
        with Session(engine) as session:
            try:
                bonus_to_update = session.query(Bonus).filter(Bonus.id == bonus_id).first()

                for key, value in data.items():
                    bonus_to_update.__setattr__(key, value)

                session.commit()
                session.flush()
                updated_bonus = bonus_to_update.to_dict()
            except Exception as e:
                session.rollback()
                return 0

        return updated_bonus

    @staticmethod
    def delete_bonuses(bonus_id):
        with Session(engine) as session:
            try:
                query = session.query(Bonus).filter(Bonus.id == bonus_id)
                query.delete()

                session.commit()
            except Exception as e:
                session.rollback()
                return 0

        return 1

    @staticmethod
    def add_new_bonus(data):
        with Session(engine) as session:
            try:
                new_bonus = Bonus(**data)
                session.add(new_bonus)
                session.flush()

                session.commit()
                created_bonus = new_bonus.to_dict()
            except Exception as e:
                session.rollback()
                return 0

        return created_bonus

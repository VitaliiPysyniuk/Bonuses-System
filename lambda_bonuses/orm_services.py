from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError

# from models import Bonus
from models.models import Bonus
from utils.database import create_db_engine

engine = create_db_engine()


class BonusesQuery:
    @staticmethod
    def get_bonuses(bonus_id=None):
        with Session(engine) as session:
            try:
                query = session.query(Bonus).order_by(Bonus.id)

                if bonus_id is not None:
                    query = query.filter(Bonus.id == bonus_id)

                query_result = query.all()
                query_result = [bonus.to_dict() for bonus in query_result]

            except SQLAlchemyError as error:
                print(error)
                return 0

        return query_result

    @staticmethod
    def get_bonus_by_id(bonus_id):
        query_result = BonusesQuery.get_bonuses(bonus_id=bonus_id)

        if query_result and len(query_result) == 1:
            bonus = query_result[0]
            return bonus

        return 0

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

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return updated_bonus

    @staticmethod
    def delete_bonuses(bonus_id):
        with Session(engine) as session:
            try:
                query = session.query(Bonus).filter(Bonus.id == bonus_id)
                query_result = query.delete()

                session.commit()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return query_result

    @staticmethod
    def add_new_bonus(data):
        with Session(engine) as session:
            try:
                new_bonus = Bonus(**data)
                session.add(new_bonus)
                session.flush()

                session.commit()
                created_bonus = new_bonus.to_dict()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return created_bonus

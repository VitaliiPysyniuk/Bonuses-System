import datetime
import sqlalchemy as db
from sqlalchemy import or_, and_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import ColumnElement as ColElem
import os

from models import RequestHistory, Request, User, Bonus

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

engine = db.create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')


class RequestQuery:
    @staticmethod
    def get_requests(request_id=None):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)
            if request_id is not None:
                query = query.filter(Request.id == request_id)

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

        return RequestQuery._parse_requests(query_result)

    @staticmethod
    def update_request(request_id, data):
        with Session(engine) as session:
            try:
                request_to_update = session.query(Request).filter(Request.id == request_id).first()

                for key, value in data.items():
                    request_to_update.__setattr__(key, value)

                session.commit()
                session.flush()
                updated_request = request_to_update.to_dict()
            except db.exc.SQLAlchemyError as e:
                session.rollback()
                return 0

        return updated_request

    @staticmethod
    def delete_request(request_id):
        with Session(engine) as session:
            try:
                query = session.query(Request).filter(Request.id == request_id)
                query_result = query.update({'status': 'deleted'})

                session.commit()
            except db.exc.SQLAlchemyError as e:
                session.rollback()
                return 0

        return query_result

    @staticmethod
    def add_new_request(data):
        with Session(engine) as session:
            try:
                new_request = Request(**data)
                session.add(new_request)
                session.flush()

                session.commit()
                created_request = new_request.to_dict()
            except db.exc.SQLAlchemyError as e:
                session.rollback()
                return 0

        return created_request

    @staticmethod
    def _parse_requests(requests):
        parsed_requests = list()

        for request in requests:
            request = dict(request)
            request_obj = request.pop('Request').to_dict()
            parsed_request = {
                **request_obj,
                **request
            }
            parsed_requests.append(parsed_request)

        return parsed_requests

    @staticmethod
    def get_filtered_requests(status, reviewer_id):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

            query = query.filter(Request.status == status)
            query = query.filter(Request.reviewer == reviewer_id)

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

        return RequestQuery._parse_requests(query_result)

    @staticmethod
    def get_worker_pending_unpaid_requests(creator_id):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

            today = datetime.datetime.today()
            today = f'{today.year}-{today.month}-{today.day}'

            query = query.filter(
                or_(Request.status == 'created', and_(Request.status == 'approved', Request.payment_date >= today)))
            query = query.filter(Request.creator == creator_id)

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

            return RequestQuery._parse_requests(query_result)

    @staticmethod
    def get_worker_approved_denied_requests(creator_id):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

            today = datetime.datetime.today()
            today = f'{today.year}-{today.month}-{today.day}'

            query = query.filter(
                or_(Request.status == 'denied', and_(Request.status == 'approved', Request.payment_date < today)))
            query = query.filter(Request.creator == creator_id)

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

            return RequestQuery._parse_requests(query_result)

    @staticmethod
    def get_worker_deleted_requests(creator_id):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

            query = query.filter(Request.status == 'deleted')
            query = query.filter(Request.creator == creator_id)

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

            return RequestQuery._parse_requests(query_result)

    @staticmethod
    def get_administrator_all_requests(query_name):
        with Session(engine) as session:
            creator = db.orm.aliased(User)
            reviewer = db.orm.aliased(User)
            query = session.query(Request, ColElem.label(Bonus.type, 'bonus_name'),
                                  ColElem.label(creator.full_name, 'creator_name'),
                                  ColElem.label(creator.slack_id, 'creator_slack_id'),
                                  ColElem.label(reviewer.full_name, 'reviewer_name'),
                                  ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

            if query_name == 'pending':
                query = query.filter(Request.status == 'created')
            elif query_name == 'unpaid':
                today = datetime.datetime.today()
                today = f'{today.year}-{today.month}-{today.day}'

                query = query.filter(and_(Request.status == 'approved',
                                          Request.payment_date >= today))
            elif query_name == 'paid':
                today = datetime.datetime.today()
                today = f'{today.year}-{today.month}-{today.day}'

                query = query.filter(and_(Request.status == 'approved',
                                          Request.payment_date < today))
            elif query_name == 'denied':
                query = query.filter(Request.status == 'denied')
            elif query_name == 'deleted':
                query = query.filter(Request.status == 'deleted')

            query_result = query.join(Bonus, Request.type_bonus == Bonus.id) \
                .join(creator, Request.creator == creator.id) \
                .join(reviewer, Request.reviewer == reviewer.id).all()

            return RequestQuery._parse_requests(query_result)


class RequestHistoryQuery:
    @staticmethod
    def get_request_history(request_id):
        with Session(engine) as session:
            query = session.query(RequestHistory).filter(RequestHistory.request_id == request_id)

            query_result = query.all()

        return RequestHistoryQuery._parse_history(query_result)

    @staticmethod
    # def add_history(data, request_id, editor, old_request=None):
    def add_history(data):
        with Session(engine) as session:
            try:
                # if old_request is not None:
                #     request = dict(old_request)
                # else:
                #     request = dict()
                #
                # changes_log = ''
                # for key in data.keys():
                #     if str(data[key]) != str(request.get(key, "-")):
                #         if key == 'reviewer' or key == 'type_bonus' or key == 'creator':
                #             continue
                #
                #         log = f'{" ".join(key.split("_")).capitalize()}:  {request.get(key, "-")}  ->  {data[key]}\n'
                #         changes_log += log

                new_history = RequestHistory(**data)
                session.add(new_history)
                session.flush()

                session.commit()
                created_history = new_history.to_dict()
            except db.exc.SQLAlchemyError as e:
                session.rollback()
                return 0

        return created_history

    @staticmethod
    def _parse_history(history):
        parsed_history = [item.to_dict() for item in history]

        return parsed_history

from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import ColumnElement as ColElem
from sqlalchemy.exc import SQLAlchemyError

from models.models import RequestHistory, Request, Worker, Bonus
from utils.database import open_db_session


class RequestQuery:
    @staticmethod
    def get_requests(request_id=None, status=None, creator_id=None, reviewer_id=None, payment_date=None,
                     payment_date_gt=None, payment_date_lt=None):

        with open_db_session() as session:
            try:
                creator = aliased(Worker)
                reviewer = aliased(Worker)
                query = session.query(Request,
                                      ColElem.label(Bonus.type, 'bonus_name'),
                                      ColElem.label(creator.full_name, 'creator_name'),
                                      ColElem.label(creator.slack_id, 'creator_slack_id'),
                                      ColElem.label(reviewer.full_name, 'reviewer_name'),
                                      ColElem.label(reviewer.slack_id, 'reviewer_slack_id')).order_by(Request.id)

                if request_id is not None:
                    query = query.filter(Request.id == request_id)
                if status is not None:
                    query = query.filter(Request.status == status)
                else:
                    query = query.filter(Request.status != 'deleted')

                if creator_id is not None:
                    query = query.filter(Request.creator == creator_id)
                if reviewer_id is not None:
                    query = query.filter(Request.reviewer == reviewer_id)
                if payment_date is not None:
                    query = query.filter(Request.payment_date == payment_date)
                if payment_date_gt is not None and payment_date_gt:
                    query = query.filter(Request.payment_date > payment_date_gt)
                if payment_date_lt is not None and payment_date_lt:
                    query = query.filter(Request.payment_date <= payment_date_lt)

                query_result = query.join(Bonus, Request.bonus_type == Bonus.id) \
                    .join(creator, Request.creator == creator.id) \
                    .join(reviewer, Request.reviewer == reviewer.id).all()

            except SQLAlchemyError as error:
                print(error)
                return 0

        return RequestQuery._parse_requests(query_result)

    @staticmethod
    def get_request_by_id(request_id):
        query_result = RequestQuery.get_requests(request_id=request_id)

        if query_result and len(query_result) == 1:
            request = query_result[0]
            return request

        return 0

    @staticmethod
    def update_request(request_id, data):
        with open_db_session() as session:
            try:
                request_to_update = session.query(Request).filter(Request.id == request_id).first()

                for key, value in data.items():
                    print(key, value)
                    request_to_update.__setattr__(key, value)

                session.commit()
                session.flush()
                updated_request = request_to_update.to_dict()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return updated_request

    @staticmethod
    def delete_request(request_id):
        with open_db_session() as session:
            try:
                query = session.query(Request).filter(Request.id == request_id)

                request_to_delete = query.first()
                if not request_to_delete:
                    return 0

                request_to_delete = request_to_delete.to_dict()
                if request_to_delete['status'] == 'deleted':
                    return 0

                query_result = query.update({'status': 'deleted'})

                session.commit()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return query_result

    @staticmethod
    def add_new_request(data):
        with open_db_session() as session:
            try:
                new_request = Request(**data)
                session.add(new_request)
                session.flush()

                session.commit()
                created_request = new_request.to_dict()

            except SQLAlchemyError as error:
                print(error)
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


class RequestHistoryQuery:
    @staticmethod
    def get_history(request_id):
        with open_db_session() as session:
            query = session.query(RequestHistory).filter(RequestHistory.request_id == request_id)

            query_result = query.all()

        return RequestHistoryQuery._parse_history(query_result)

    @staticmethod
    def add_history(data):
        with open_db_session() as session:
            try:
                new_history = RequestHistory(**data)
                session.add(new_history)
                session.flush()

                session.commit()
                created_history = new_history.to_dict()

            except SQLAlchemyError as error:
                print(error)
                session.rollback()
                return 0

        return created_history

    @staticmethod
    def _parse_history(history):
        parsed_history = [item.to_dict() for item in history]

        return parsed_history

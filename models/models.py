from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(50), unique=True, nullable=False)
    position = Column(String(100))
    slack_id = Column(String(11), unique=True, nullable=False)

    workers_roles_rel = relationship("WorkersRolesRelation", back_populates='worker_rel')

    def __init__(self, full_name, slack_id, position=''):
        self.full_name = full_name
        self.position = position
        self.slack_id = slack_id

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'position': self.position,
            'slack_id': self.slack_id
        }


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role_name = Column(String(20), nullable=False)

    roles_workers_rel = relationship("WorkersRolesRelation", back_populates='role_rel')

    def __init__(self, role_name):
        self.role_name = role_name


class WorkersRolesRelation(Base):
    __tablename__ = "workers_roles_relations"

    id = Column(Integer, primary_key=True)

    worker_id = Column(Integer, ForeignKey('workers.id', ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"))

    worker_rel = relationship("Worker", back_populates="workers_roles_rel")
    role_rel = relationship("Role", back_populates="roles_workers_rel")

    def __init__(self, worker_id, role_id):
        self.worker_id = worker_id
        self.role_id = role_id


class Bonus(Base):
    __tablename__ = "bonuses_types"

    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    description = Column(String(100))

    requests_rel = relationship("Request", back_populates="bonus_type_rel")

    def __init__(self, type, description=""):
        self.type = type
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description
        }


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    status = Column(String(20), nullable=False, default='created')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())
    payment_date = Column(Date)
    payment_amount = Column(Integer, default=1)
    description = Column(String(100))

    creator = Column(Integer, ForeignKey('workers.id', ondelete="SET NULL"))
    reviewer = Column(Integer, ForeignKey('workers.id', ondelete="SET NULL"))
    bonus_type = Column(Integer, ForeignKey('bonuses_types.id', ondelete="SET NULL"))

    creator_worker_rel = relationship("Worker", foreign_keys="Request.creator")
    reviewer_worker_rel = relationship("Worker", foreign_keys="Request.reviewer")
    bonus_type_rel = relationship("Bonus", back_populates="requests_rel")
    request_history_rel = relationship("RequestHistory", back_populates="requests_rel")

    def __init__(self, creator, reviewer, bonus_type, payment_amount, payment_date, status="", description=""):
        self.creator = creator
        self.reviewer = reviewer
        self.bonus_type = bonus_type
        self.payment_amount = payment_amount
        self.payment_date = payment_date
        self.status = status
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'creator': self.creator,
            'reviewer': self.reviewer,
            'bonus_type': self.bonus_type,
            'payment_amount': self.payment_amount,
            'payment_date': str(self.payment_date),
            'status': self.status,
            'description': self.description,
            'created_at': str(self.created_at)
        }


class RequestHistory(Base):
    __tablename__ = "requests_history"

    id = Column(Integer, primary_key=True)
    changes = Column(String(300), nullable=False, default='created')
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    editor = Column(String(50), nullable=False)

    request_id = Column(Integer, ForeignKey('requests.id'))

    requests_rel = relationship("Request", back_populates="request_history_rel")

    def __init__(self, request_id, changes, editor):
        self.request_id = request_id
        self.changes = changes
        self.editor = editor

    def to_dict(self):
        return {
            'id': self.id,
            'changes': self.changes,
            'editor': self.editor,
            'timestamp': str(self.timestamp),
            'request_id': self.request_id
        }

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(50), unique=True, nullable=False)
    position = Column(String(100))
    slack_id = Column(String(11), unique=True, nullable=False)

    users_roles = relationship("UsersRolesRelation", back_populates='user')

    def __init__(self, full_name, slack_id, position=''):
        self.full_name = full_name
        self.position = position
        self.slack_id = slack_id

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.full_name,
            'position': self.position,
            'slack_id': self.slack_id
        }


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role_name = Column(String(20), nullable=False)

    roles_users = relationship("UsersRolesRelation", back_populates='role')

    def __init__(self, role_name):
        self.role_name = role_name


class UsersRolesRelation(Base):
    __tablename__ = "users_roles_relation"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"))

    user = relationship("User", back_populates="users_roles")
    role = relationship("Roles", back_populates="roles_users")

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id


class Bonus(Base):
    __tablename__ = "type_bonus"
    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    description = Column(String(100))

    requests = relationship("Request", back_populates="bonus_type")

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
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    payment_date = Column(Date)
    payment_amount = Column(Integer, default=1)
    description = Column(String(100))

    creator = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"))
    reviewer = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"))
    type_bonus = Column(Integer, ForeignKey('type_bonus.id', ondelete="SET NULL"))

    creator_user = relationship("User", foreign_keys="Request.creator")
    reviewer_user = relationship("User", foreign_keys="Request.reviewer")
    bonus_type = relationship("Bonus", back_populates="requests")
    request_history = relationship("RequestHistory", back_populates="requests")

    def __init__(self, creator, reviewer, type_bonus, payment_amount, payment_date, status="", description=""):
        self.creator = creator
        self.reviewer = reviewer
        self.type_bonus = type_bonus
        self.payment_amount = payment_amount
        self.payment_date = payment_date
        self.status = status
        self.description = description


class RequestHistory(Base):
    __tablename__ = "requests_history"
    id = Column(Integer, primary_key=True)
    changes = Column(String(300), nullable=False, default='created')
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    editor = Column(String(50), nullable=False)

    request_id = Column(Integer, ForeignKey('requests.id'))

    requests = relationship("Request", back_populates="request_history")

    def __init__(self, request_id, changes, editor):
        self.request_id = request_id
        self.changes = changes
        self.editor = editor

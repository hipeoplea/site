import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import db


class Teams(db):
    __tablename__ = 'Teams'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(64), unique=True)
    points = sa.Column(sa.Integer, default=0)
    password_hash = sa.Column(sa.Integer, unique=True)

    teams = sa.orm.relation('User', lazy='dynamic', primaryjoin="Teams.id == User.team")


class User(db, UserMixin):
    __tablename__ = 'User'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(64), unique=True, index=True)
    role = sa.Column(sa.Integer, default=0)
    team = sa.Column(sa.Integer, sa.ForeignKey('Teams.id'))


class Tasks(db):
    __tablename__ = 'tasks'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    body = sa.Column(sa.String, unique=True)
    test = sa.Column(sa.String, unique=True)
    max_price = sa.Column(sa.Integer)
    coords = sa.Column(sa.String)

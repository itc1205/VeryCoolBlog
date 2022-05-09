from datetime import datetime as dt

from flask_login import UserMixin

import sqlalchemy
from sqlalchemy import orm

from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.now)
    description = sqlalchemy.Column(sqlalchemy.String)
    
    news = orm.relation("News", back_populates='user', lazy="dynamic")

    profile_image = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'---\nUser with id - {self.id}\n--- {self.name} {self.surname}\n---'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

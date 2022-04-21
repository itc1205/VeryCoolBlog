from datetime import datetime as dt

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class SubEmail(SqlAlchemyBase):
    __tablename__ = "SubEmail"
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
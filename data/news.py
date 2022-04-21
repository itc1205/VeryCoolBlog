from datetime import datetime as dt

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    short_description = sqlalchemy.Column(sqlalchemy.String)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=dt.now)
    
    header_img = sqlalchemy.Column(sqlalchemy.String)
    
    preview_img = sqlalchemy.Column(sqlalchemy.String)
    
    views_count = sqlalchemy.Column(sqlalchemy.Integer, default = 0)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relation('User')

    def __repr__(self):
        print(f' - {self.user.name} {self.user.surname} - created a post with id {self.id} at  {self.created_date}')
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
    
    tag = sqlalchemy.Column(sqlalchemy.String, default=None)

    short_description = sqlalchemy.Column(sqlalchemy.String)
    ##############################
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=dt.now)

    created_date_string = sqlalchemy.Column(sqlalchemy.String, default=lambda: dt.now().strftime("%d %b %Y"))
    ##############################
    header_img = sqlalchemy.Column(sqlalchemy.String)
    
    preview_img = sqlalchemy.Column(sqlalchemy.String)
    ##############################
    views_count = sqlalchemy.Column(sqlalchemy.Integer, default = 0)
    ##############################
    reading_time_in_seconds = sqlalchemy.Column(sqlalchemy.Integer) # This parameter is for sorting by time

    reading_time_in_minutes = sqlalchemy.Column(sqlalchemy.Integer) # This parameter is for showing in the post (so we dont need to calculate it each time)
    ##############################
    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship('User', lazy="dynamic")

    def __repr__(self):
        print(f' - {self.user.name} {self.user.surname} - created a post with id {self.id} at  {self.created_date}')
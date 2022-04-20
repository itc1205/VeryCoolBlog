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
    
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=dt.now)
    
    header_img = sqlalchemy.Column(sqlalchemy.String)
    
    preview_img = sqlalchemy.Column(sqlalchemy.String)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relation('User')

"""
    @Author: ImYrS Yang
    @Date: 2023/6/27
    @Copyright: @ImYrS
"""

from peewee import *

from modules.types import LoginRequestState

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class LoginRequest(BaseModel):
    id = PrimaryKeyField()
    uuid = CharField(255, unique=True)
    t = CharField(32)
    ck = CharField(128)
    content = TextField()
    state = IntegerField(default=LoginRequestState.Pending)
    created_at = BigIntegerField(default=0)

    class Meta:
        table_name = 'login'

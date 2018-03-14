import datetime

from peewee import *


DATABASE = SqliteDatabase('work_log.db')


class Task(Model):
    employee = CharField(max_length=60)
    duration = IntegerField()
    title = CharField(max_length=140)
    notes = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

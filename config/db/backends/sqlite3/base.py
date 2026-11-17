from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper

from .operations import DatabaseOperations


class DatabaseWrapper(SQLiteDatabaseWrapper):
    ops_class = DatabaseOperations

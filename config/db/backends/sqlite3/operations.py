from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.backends.sqlite3.operations import (
    DatabaseOperations as SQLiteDatabaseOperations,
)
from django.utils import timezone


class DatabaseOperations(SQLiteDatabaseOperations):
    def convert_datetimefield_value(self, value, expression, connection):
        value = super().convert_datetimefield_value(
            value,
            expression,
            connection,
        )
        if value is not None and settings.USE_TZ:
            value = timezone.localtime(value, ZoneInfo(settings.TIME_ZONE))
        return value

    def adapt_datetimefield_value(self, value):
        if value is None:
            return None
        if not isinstance(value, datetime):
            return value

        local_timezone = ZoneInfo(settings.TIME_ZONE)
        if timezone.is_aware(value):
            value = timezone.localtime(value, local_timezone)
        elif settings.USE_TZ:
            value = timezone.make_aware(value, local_timezone)

        return value.isoformat(sep=' ')

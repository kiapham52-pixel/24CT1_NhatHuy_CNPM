from datetime import timezone as datetime_timezone
from zoneinfo import ZoneInfo

from django.db import migrations
from django.utils.dateparse import parse_datetime


LOCAL_TIME_ZONE = ZoneInfo('Asia/Ho_Chi_Minh')


def _update_datetime_values(apps, schema_editor, to_local):
    connection = schema_editor.connection
    quote_name = connection.ops.quote_name

    with connection.cursor() as cursor:
        tables = connection.introspection.get_table_list(cursor)
        for table in tables:
            if table.type != 't':
                continue

            description = connection.introspection.get_table_description(
                cursor,
                table.name,
            )
            datetime_columns = [
                column.name
                for column in description
                if (column.type_code or '').lower() == 'datetime'
            ]

            for column in datetime_columns:
                quoted_table = quote_name(table.name)
                quoted_column = quote_name(column)
                cursor.execute(
                    f'SELECT rowid, {quoted_column} '
                    f'FROM {quoted_table} '
                    f'WHERE {quoted_column} IS NOT NULL'
                )
                rows = cursor.fetchall()

                for row_id, stored_value in rows:
                    value = (
                        parse_datetime(stored_value)
                        if isinstance(stored_value, str)
                        else stored_value
                    )
                    if value is None:
                        raise ValueError(
                            f'Cannot parse {table.name}.{column} value '
                            f'{stored_value!r}'
                        )

                    if to_local:
                        if value.utcoffset() is None:
                            value = value.replace(tzinfo=datetime_timezone.utc)
                        value = value.astimezone(LOCAL_TIME_ZONE)
                    else:
                        if value.utcoffset() is None:
                            value = value.replace(tzinfo=LOCAL_TIME_ZONE)
                        value = value.astimezone(datetime_timezone.utc)
                        value = value.replace(tzinfo=None)

                    cursor.execute(
                        f'UPDATE {quoted_table} '
                        f'SET {quoted_column} = %s WHERE rowid = %s',
                        (value.isoformat(sep=' '), row_id),
                    )


def convert_utc_to_local(apps, schema_editor):
    _update_datetime_values(apps, schema_editor, to_local=True)


def convert_local_to_utc(apps, schema_editor):
    _update_datetime_values(apps, schema_editor, to_local=False)


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0010_order_note'),
    ]

    operations = [
        migrations.RunPython(
            convert_utc_to_local,
            reverse_code=convert_local_to_utc,
        ),
    ]

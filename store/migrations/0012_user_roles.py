from django.conf import settings
from django.db import migrations


ADMIN_GROUP = 'ADMIN'
CUSTOMER_GROUP = 'CUSTOMER'


def create_roles_and_assign_users(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    database = schema_editor.connection.alias

    admin_group, _ = Group.objects.using(database).get_or_create(
        name=ADMIN_GROUP
    )
    customer_group, _ = Group.objects.using(database).get_or_create(
        name=CUSTOMER_GROUP
    )

    managed_models = [
        settings.AUTH_USER_MODEL.split('.'),
        ('store', 'product'),
        ('store', 'order'),
        ('store', 'orderitem'),
        ('store', 'profile'),
    ]
    admin_permissions = []

    for app_label, model_name in managed_models:
        content_type, _ = ContentType.objects.using(database).get_or_create(
            app_label=app_label,
            model=model_name.lower(),
        )
        for action in ('add', 'change', 'delete', 'view'):
            permission, _ = Permission.objects.using(database).get_or_create(
                content_type=content_type,
                codename=f'{action}_{model_name.lower()}',
                defaults={
                    'name': f'Can {action} {model_name.replace("_", " ")}',
                },
            )
            admin_permissions.append(permission)

    admin_group.permissions.add(*admin_permissions)

    for user in User.objects.using(database).all().iterator():
        group = admin_group if user.is_staff or user.is_superuser else customer_group
        user.groups.add(group)


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0011_localize_datetime_storage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            create_roles_and_assign_users,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

from django.contrib.auth.models import Group


ADMIN_GROUP = 'ADMIN'
CUSTOMER_GROUP = 'CUSTOMER'


def assign_user_role(user, *, is_staff):
    role_group = Group.objects.get(
        name=ADMIN_GROUP if is_staff else CUSTOMER_GROUP
    )
    other_group = Group.objects.get(
        name=CUSTOMER_GROUP if is_staff else ADMIN_GROUP
    )
    user.groups.add(role_group)
    user.groups.remove(other_group)

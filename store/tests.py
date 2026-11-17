from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product, Profile
from .roles import ADMIN_GROUP, CUSTOMER_GROUP


class UserRoleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.get(name=ADMIN_GROUP)
        cls.customer_group = Group.objects.get(name=CUSTOMER_GROUP)

        cls.customer = User.objects.create_user(
            username='customer',
            password='Customer-pass-123',
        )
        cls.customer.groups.add(cls.customer_group)

        cls.other_customer = User.objects.create_user(
            username='other-customer',
            password='Other-pass-123',
        )
        cls.other_customer.groups.add(cls.customer_group)

        cls.staff_admin = User.objects.create_user(
            username='staff-admin',
            password='Staff-pass-123',
            is_staff=True,
        )
        cls.staff_admin.groups.add(cls.admin_group)

        cls.product = Product.objects.create(
            name='Test instrument',
            category='Guitar',
            price=1000,
            image='https://example.com/instrument.jpg',
            description='Test product',
            quantity=5,
        )
        cls.customer_order = Order.objects.create(
            user=cls.customer,
            customer_name='Customer',
            phone='0900000001',
            address='Customer address',
            total=1000,
        )
        cls.other_order = Order.objects.create(
            user=cls.other_customer,
            customer_name='Other customer',
            phone='0900000002',
            address='Other address',
            total=1000,
        )

    def test_registration_creates_customer_without_admin_privileges(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new-customer',
                'email': 'new-customer@example.com',
                'full_name': 'New Customer',
                'date_of_birth': '2000-01-01',
                'password1': 'New-customer-pass-123',
                'password2': 'New-customer-pass-123',
            },
        )

        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='new-customer')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.groups.filter(name=CUSTOMER_GROUP).exists())
        self.assertTrue(user.check_password('New-customer-pass-123'))
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_customer_cannot_open_admin_or_manage_products(self):
        self.client.force_login(self.customer)

        admin_response = self.client.get('/admin/')
        product_admin_response = self.client.get('/admin/store/product/add/')

        self.assertIn(admin_response.status_code, (302, 403))
        self.assertIn(product_admin_response.status_code, (302, 403))
        self.assertFalse(self.customer.has_perm('store.add_product'))

    def test_customer_can_only_access_their_own_orders_and_profile(self):
        self.client.force_login(self.customer)

        self.assertEqual(
            self.client.get(
                reverse('order_detail', args=[self.customer_order.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse('order_detail', args=[self.other_order.pk])
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse('payment_qr', args=[self.other_order.pk])
            ).status_code,
            404,
        )

        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.context['profile'].user, self.customer)

    def test_admin_group_has_store_management_permissions(self):
        self.assertTrue(self.staff_admin.has_perm('store.add_product'))
        self.assertTrue(self.staff_admin.has_perm('store.change_order'))
        self.assertTrue(self.staff_admin.has_perm('auth.view_user'))

        self.client.force_login(self.staff_admin)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(
            self.client.get('/admin/store/product/add/').status_code,
            200,
        )

    def test_staff_admin_cannot_promote_accounts_or_manage_staff_users(self):
        self.client.force_login(self.staff_admin)
        add_user_url = reverse('admin:auth_user_add')
        response = self.client.post(
            add_user_url,
            {
                'username': 'managed-customer',
                'password1': 'Managed-customer-pass-123',
                'password2': 'Managed-customer-pass-123',
                'is_staff': 'on',
                'is_superuser': 'on',
            },
        )

        self.assertIn(response.status_code, (200, 302))
        user = User.objects.get(username='managed-customer')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.groups.filter(name=CUSTOMER_GROUP).exists())

        staff_user_url = reverse(
            'admin:auth_user_change',
            args=[self.staff_admin.pk],
        )
        self.assertIn(
            self.client.get(staff_user_url).status_code,
            (302, 403, 404),
        )

        customer_user_url = reverse(
            'admin:auth_user_change',
            args=[self.customer.pk],
        )
        self.assertEqual(self.client.get(customer_user_url).status_code, 200)

    def test_customer_group_has_no_management_permissions(self):
        self.assertFalse(self.customer.has_perm('store.add_product'))
        self.assertFalse(self.customer.has_perm('store.change_order'))
        self.assertFalse(self.customer.has_perm('auth.view_user'))

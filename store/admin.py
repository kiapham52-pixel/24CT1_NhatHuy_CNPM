from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Product, Order, OrderItem, Profile
from .roles import ADMIN_GROUP, assign_user_role


# =========================================================
# QUẢN LÝ TÀI KHOẢN KHÁCH HÀNG
# =========================================================

class CustomUserAdmin(UserAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'role',
        'date_joined',
        'last_login',
        'is_active',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'groups',
        'date_joined',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    ordering = (
        '-date_joined',
    )

    readonly_fields = (
        'date_joined',
        'last_login',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(
                is_staff=False,
                is_superuser=False,
            )
        return queryset

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        if obj is None:
            return self.add_fieldsets
        return (
            (None, {'fields': ('username', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
            ('Account status', {'fields': ('is_active',)}),
        )

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        assign_user_role(form.instance, is_staff=(
            form.instance.is_staff or form.instance.is_superuser
        ))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and super().has_delete_permission(
            request,
            obj,
        )

    @admin.display(description='Vai trò')
    def role(self, obj):
        return ADMIN_GROUP if obj.is_staff or obj.is_superuser else 'CUSTOMER'


# Django đã đăng ký User mặc định
# nên phải hủy đăng ký trước
admin.site.unregister(User)

# Đăng ký lại với giao diện tùy chỉnh
admin.site.register(User, CustomUserAdmin)


# =========================================================
# FORM CHỈNH SỬA ORDER
# =========================================================

class OrderAdminForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = '__all__'

    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        required=True,
        label='Trạng thái',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 250px; padding: 8px;'
            }
        )
    )


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'quantity',
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
        'category',
    )


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        'product',
        'quantity',
        'price',
    )


# =========================================================
# ORDER
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    form = OrderAdminForm

    list_display = (
        'id',
        'user',
        'customer_name',
        'phone',
        'address',
        'total',
        'colored_status',
        'created_at',
    )

    fields = (
        'user',
        'customer_name',
        'phone',
        'address',
        'note',
        'total',
        'status',
        'created_at',
    )

    search_fields = (
        'user__username',
        'customer_name',
        'phone',
        'address',
    )

    list_filter = (
        'status',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )

    inlines = [
        OrderItemInline
    ]

    ordering = (
        '-created_at',
    )

    @admin.display(description='Trạng thái')
    def colored_status(self, obj):

        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'shipping': '#8b5cf6',
            'completed': '#22c55e',
            'cancelled': '#ef4444',
        }

        labels = {
            'pending': '🟡 Chờ xác nhận',
            'confirmed': '🔵 Đã xác nhận',
            'shipping': '🟣 Đang giao',
            'completed': '🟢 Đã giao',
            'cancelled': '🔴 Đã hủy',
        }

        color = colors.get(
            obj.status,
            '#6b7280'
        )

        label = labels.get(
            obj.status,
            obj.status
        )

        return format_html(
            '<span style="'
            'background-color: {};'
            'color: white;'
            'padding: 5px 12px;'
            'border-radius: 20px;'
            'font-weight: 600;'
            'display: inline-block;'
            '">{}</span>',
            color,
            label
        )


# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )

    search_fields = (
        'product__name',
        'order__customer_name',
        'order__user__username',
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'date_of_birth',
    )

    search_fields = (
        'user__username',
        'user__email',
        'full_name',
        'phone',
    )
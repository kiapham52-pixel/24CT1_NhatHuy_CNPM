from django.db import models
from django.contrib.auth.models import User


# =========================================================
# PRODUCT - SẢN PHẨM
# =========================================================

class Product(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Tên sản phẩm'
    )

    category = models.CharField(
        max_length=100,
        verbose_name='Danh mục'
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Giá'
    )

    image = models.URLField(
        verbose_name='Link hình ảnh'
    )

    description = models.TextField(
        verbose_name='Mô tả'
    )

    quantity = models.IntegerField(
        default=0,
        verbose_name='Số lượng'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'


# =========================================================
# ORDER - ĐƠN HÀNG
# =========================================================

class Order(models.Model):

    STATUS_CHOICES = [

        (
            'pending',
            '🟡 Chờ xác nhận'
        ),

        (
            'confirmed',
            '🔵 Đã xác nhận'
        ),

        (
            'shipping',
            '🟣 Đang giao'
        ),

        (
            'completed',
            '🟢 Đã giao'
        ),

        (
            'cancelled',
            '🔴 Đã hủy'
        ),
    ]

    # -----------------------------------------------------
    # TÀI KHOẢN KHÁCH HÀNG
    # -----------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Tài khoản'
    )

    # -----------------------------------------------------
    # THÔNG TIN KHÁCH HÀNG
    # -----------------------------------------------------

    customer_name = models.CharField(
        max_length=200,
        verbose_name='Tên khách hàng'
    )

    phone = models.CharField(
        max_length=20,
        verbose_name='Số điện thoại'
    )

    address = models.TextField(
        verbose_name='Địa chỉ'
    )

    note = models.TextField(
        blank=True,
        default='',
        verbose_name='Ghi chú'
    )

    # -----------------------------------------------------
    # TỔNG TIỀN
    # -----------------------------------------------------

    total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Tổng tiền'
    )

    # -----------------------------------------------------
    # TRẠNG THÁI
    # -----------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )

    # -----------------------------------------------------
    # NGÀY ĐẶT HÀNG
    # -----------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày đặt hàng'
    )

    def __str__(self):

        if self.user:
            return (
                f"Đơn hàng #{self.id} - "
                f"{self.user.username}"
            )

        return (
            f"Đơn hàng #{self.id} - "
            f"{self.customer_name}"
        )

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']


# =========================================================
# ORDER ITEM - CHI TIẾT ĐƠN HÀNG
# =========================================================

class OrderItem(models.Model):

    # -----------------------------------------------------
    # ĐƠN HÀNG
    # -----------------------------------------------------

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Đơn hàng'
    )

    # -----------------------------------------------------
    # SẢN PHẨM
    # -----------------------------------------------------

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Sản phẩm'
    )

    # -----------------------------------------------------
    # SỐ LƯỢNG
    # -----------------------------------------------------

    quantity = models.IntegerField(
        default=1,
        verbose_name='Số lượng'
    )

    # -----------------------------------------------------
    # GIÁ
    # -----------------------------------------------------

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Giá'
    )

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"{self.quantity}"
        )

    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'


# =========================================================
# PROFILE - THÔNG TIN KHÁCH HÀNG
# =========================================================

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Tài khoản'
    )

    full_name = models.CharField(
        max_length=200,
        verbose_name='Họ và tên'
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ngày sinh'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Số điện thoại'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Ảnh đại diện'
    )

    def __str__(self):
        return f"{self.full_name} - {self.user.username}"

    class Meta:
        verbose_name = 'Thông tin khách hàng'
        verbose_name_plural = 'Thông tin khách hàng'
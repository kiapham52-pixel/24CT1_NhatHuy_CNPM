from django.contrib import admin
from django.urls import path
from store.views import profile, profile_edit

from django.conf import settings
from django.conf.urls.static import static


from store.views import (
    order_list,
    order_detail,
    order_success,
    payment_qr,
)
from store.views import (
    home,
    product_detail,
    cart,
    add_to_cart,
    increase_cart,
    decrease_cart,
    remove_from_cart,
    checkout,
    order_list,
    register,
    login_view,
    logout_view,
    profile,
)


urlpatterns = [

    # =========================
    # ADMIN
    # =========================

    path(
        'admin/',
        admin.site.urls
    ),


    # =========================
    # TRANG CHỦ
    # =========================

    path(
        '',
        home,
        name='home'
    ),

    path(
        'products/',
        home,
        name='products'
    ),


    # =========================
    # SẢN PHẨM
    # =========================

    path(
        'product/<int:id>/',
        product_detail,
        name='product_detail'
    ),


    # =========================
    # GIỎ HÀNG
    # =========================

    path(
        'cart/',
        cart,
        name='cart'
    ),

    path(
        'cart/add/<int:id>/',
        add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/increase/<int:id>/',
        increase_cart,
        name='increase_cart'
    ),

    path(
        'cart/decrease/<int:id>/',
        decrease_cart,
        name='decrease_cart'
    ),

    path(
        'cart/remove/<int:id>/',
        remove_from_cart,
        name='remove_from_cart'
    ),


    # =========================
    # THANH TOÁN
    # =========================

    path(
        'checkout/',
        checkout,
        name='checkout'
    ),


    # =========================
    # ĐƠN HÀNG
    # =========================

    path(
        'orders/',
        order_list,
        name='order_list'
    ),

    path(
    'orders/<int:id>/',
    order_detail,
    name='order_detail'
),

    path(
        'orders/success/<int:id>/',
        order_success,
        name='order_success'
    ),

    path(
        'orders/payment/<int:id>/',
        payment_qr,
        name='payment_qr'
    ),


    # =========================
    # TÀI KHOẢN
    # =========================

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    path(
        'profile/',
        profile,
        name='profile'
    ),

    path('profile/', profile, name='profile'),


    path('profile/edit/', profile_edit, name='profile_edit'),

]


# =========================================================
# HIỂN THỊ MEDIA KHI DEBUG
# =========================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
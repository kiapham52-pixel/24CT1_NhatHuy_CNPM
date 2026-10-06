from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, Profile

from .forms import RegisterForm,ProfileForm

from .models import (
    Product,
    Order,
    OrderItem,
    Profile
)


# =========================================================
# TRANG CHỦ
# =========================================================

def home(request):

    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    if selected_category:
        products = products.filter(category=selected_category)

    categories = Product.objects.values('category').annotate(
        product_count=Count('id')
    ).order_by('category')

    return render(
        request,
        'home.html',
        {
            'products': products,
            'categories': categories,
            'search_query': search_query,
            'selected_category': selected_category,
        }
    )


# =========================================================
# CHI TIẾT SẢN PHẨM
# =========================================================

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    return render(
        request,
        'product_detail.html',
        {
            'product': product
        }
    )


# =========================================================
# GIỎ HÀNG
# =========================================================

def cart(request):

    cart_data = request.session.get(
        'cart',
        {}
    )

    products = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id
        )

        subtotal = product.price * quantity

        total += subtotal

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(
        request,
        'cart.html',
        {
            'products': products,
            'total': total
        }
    )


# =========================================================
# THÊM SẢN PHẨM VÀO GIỎ
# =========================================================

def add_to_cart(request, id):

    cart_data = request.session.get(
        'cart',
        {}
    )

    product_id = str(id)

    cart_data[product_id] = (
        cart_data.get(product_id, 0) + 1
    )

    request.session['cart'] = cart_data

    return redirect('cart')


# =========================================================
# TĂNG SỐ LƯỢNG
# =========================================================

def increase_cart(request, id):

    cart_data = request.session.get(
        'cart',
        {}
    )

    product_id = str(id)

    cart_data[product_id] = (
        cart_data.get(product_id, 0) + 1
    )

    request.session['cart'] = cart_data

    return redirect('cart')


# =========================================================
# GIẢM SỐ LƯỢNG
# =========================================================

def decrease_cart(request, id):

    cart_data = request.session.get(
        'cart',
        {}
    )

    product_id = str(id)

    if product_id in cart_data:

        cart_data[product_id] -= 1

        if cart_data[product_id] <= 0:

            del cart_data[product_id]

    request.session['cart'] = cart_data

    return redirect('cart')


# =========================================================
# XÓA SẢN PHẨM KHỎI GIỎ
# =========================================================

def remove_from_cart(request, id):

    cart_data = request.session.get(
        'cart',
        {}
    )

    product_id = str(id)

    if product_id in cart_data:

        del cart_data[product_id]

    request.session['cart'] = cart_data

    return redirect('cart')


# =========================================================
# THANH TOÁN
# =========================================================

@login_required(login_url='login')
def checkout(request):

    cart_data = request.session.get(
        'cart',
        {}
    )

    # -----------------------------------------------------
    # GIỎ HÀNG TRỐNG
    # -----------------------------------------------------

    if not cart_data:

        return redirect('cart')


    products = []


    # -----------------------------------------------------
    # LẤY SẢN PHẨM TRONG GIỎ
    # -----------------------------------------------------

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id
            )

            # ---------------------------------------------
            # KIỂM TRA SỐ LƯỢNG KHO
            # ---------------------------------------------

            subtotal = (
                product.price * quantity
            )


            products.append({

                'product': product,

                'quantity': quantity,

                'subtotal': subtotal

            })


        except Product.DoesNotExist:

            pass


    # -----------------------------------------------------
    # KIỂM TRA SAU KHI LỌC SẢN PHẨM
    # -----------------------------------------------------

    if not products:

        request.session['cart'] = {}

        return redirect('cart')


    # -----------------------------------------------------
    # TÍNH TỔNG TIỀN
    # -----------------------------------------------------

    total = sum(
        item['subtotal']
        for item in products
    )


    # =====================================================
    # ĐẶT HÀNG
    # =====================================================

    if request.method == 'POST':

        customer_name = request.POST.get(
            'customer_name',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        note = request.POST.get(
            'note',
            ''
        ).strip()

        # -------------------------------------------------
        # LẤY PHƯƠNG THỨC THANH TOÁN
        # -------------------------------------------------

        payment_method = request.POST.get(
            'payment_method',
            'cod'
        )


        # -------------------------------------------------
        # KIỂM TRA THÔNG TIN
        # -------------------------------------------------

        if not customer_name:

            return render(
                request,
                'checkout.html',
                {
                    'products': products,
                    'total': total,
                    'error':
                        'Vui lòng nhập họ tên!'
                }
            )


        if not phone:

            return render(
                request,
                'checkout.html',
                {
                    'products': products,
                    'total': total,
                    'error':
                        'Vui lòng nhập số điện thoại!'
                }
            )


        if not address:

            return render(
                request,
                'checkout.html',
                {
                    'products': products,
                    'total': total,
                    'error':
                        'Vui lòng nhập địa chỉ!'
                }
            )


        # -------------------------------------------------
        # KIỂM TRA PHƯƠNG THỨC THANH TOÁN
        # -------------------------------------------------

        if payment_method not in ['cod', 'bank']:

            payment_method = 'cod'


        try:
            with transaction.atomic():
                locked_products = []
                final_total = 0

                for product_id, requested_quantity in cart_data.items():
                    product = Product.objects.select_for_update().get(
                        id=product_id
                    )
                    quantity = int(requested_quantity)

                    if quantity <= 0 or quantity > product.quantity:
                        raise ValueError(
                            f'Sản phẩm "{product.name}" không đủ tồn kho.'
                        )

                    locked_products.append((product, quantity))
                    final_total += product.price * quantity

                if not locked_products:
                    raise ValueError('Giỏ hàng không có sản phẩm hợp lệ.')

                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    note=note,
                    total=final_total,
                    status='pending'
                )

                for product, quantity in locked_products:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    product.quantity -= quantity
                    product.save(update_fields=['quantity'])

        except (Product.DoesNotExist, ValueError) as error:
            return render(
                request,
                'checkout.html',
                {
                    'products': products,
                    'total': total,
                    'error': str(error),
                }
            )

        request.session['cart'] = {}
        request.session.modified = True


        # =================================================
        # THANH TOÁN TIỀN MẶT
        # =================================================

        if payment_method == 'cod':

            return redirect('order_success', id=order.id)


        # =================================================
        # THANH TOÁN CHUYỂN KHOẢN
        # =================================================

        # -------------------------------------------------
        # THÔNG TIN TÀI KHOẢN SHOP
        # -------------------------------------------------
        # ⚠️ BẠN ĐỔI 3 DÒNG NÀY THÀNH
        # THÔNG TIN NGÂN HÀNG CỦA BẠN
        # -------------------------------------------------

        bank_id = 'MB'

        account_no = '0123456789'

        account_name = 'MUSICSTORE'


        # -------------------------------------------------
        # NỘI DUNG CHUYỂN KHOẢN
        # -------------------------------------------------

        transfer_content = (
            f'MUSICSTORE DH{order.id}'
        )


        # -------------------------------------------------
        # TẠO LINK QR VIETQR
        # -------------------------------------------------

        qr_url = (

            f'https://img.vietqr.io/image/'
            f'{bank_id}-{account_no}-compact2.png'
            f'?amount={int(total)}'
            f'&addInfo={transfer_content}'
            f'&accountName={account_name}'

        )


        # -------------------------------------------------
        # HIỂN THỊ TRANG QR
        # -------------------------------------------------

        return redirect('payment_qr', id=order.id)


    # =====================================================
    # HIỂN THỊ TRANG CHECKOUT
    # =====================================================

    return render(

        request,

        'checkout.html',

        {
            'products': products,

            'total': total
        }

    )

# =========================================================
# DANH SÁCH ĐƠN HÀNG CỦA KHÁCH HÀNG
# =========================================================

@login_required(login_url='login')
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'orders.html',
        {
            'orders': orders
        }
    )


# =========================================================
# CHI TIẾT ĐƠN HÀNG
# =========================================================

@login_required(login_url='login')
def order_detail(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    )

    return render(
        request,
        'order_detail.html',
        {
            'order': order,
            'items': items
        }
    )


@login_required(login_url='login')
def order_success(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    return render(
        request,
        'order_success.html',
        {
            'order': order
        }
    )

# =========================================================
# ĐĂNG KÝ TÀI KHOẢN
# =========================================================

def register(request):

    # -----------------------------------------------------
    # NẾU ĐÃ ĐĂNG NHẬP
    # -----------------------------------------------------

    if request.user.is_authenticated:

        return redirect('home')


    # -----------------------------------------------------
    # KHI SUBMIT FORM
    # -----------------------------------------------------

    if request.method == 'POST':

        form = RegisterForm(
            request.POST,
            request.FILES
        )


        # -------------------------------------------------
        # KIỂM TRA FORM
        # -------------------------------------------------

        if form.is_valid():


            # =============================================
            # TẠO USER
            # =============================================

            user = form.save()


            # =============================================
            # TẠO PROFILE
            # =============================================

            Profile.objects.create(

                user=user,

                full_name=form.cleaned_data[
                    'full_name'
                ],

                date_of_birth=form.cleaned_data[
                    'date_of_birth'
                ],

                avatar=form.cleaned_data.get(
                    'avatar'
                )

            )


            # =============================================
            # ĐĂNG NHẬP NGAY
            # =============================================

            login(
                request,
                user
            )


            # =============================================
            # CHUYỂN VỀ TRANG CHỦ
            # =============================================

            return redirect('home')


    # -----------------------------------------------------
    # HIỂN THỊ FORM
    # -----------------------------------------------------

    else:

        form = RegisterForm()


    return render(
        request,
        'register.html',
        {
            'form': form
        }
    )


# =========================================================
# ĐĂNG NHẬP
# =========================================================

def login_view(request):

    # -----------------------------------------------------
    # NẾU ĐÃ ĐĂNG NHẬP
    # -----------------------------------------------------

    if request.user.is_authenticated:

        return redirect('home')


    # -----------------------------------------------------
    # SUBMIT FORM
    # -----------------------------------------------------

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )


        # -------------------------------------------------
        # XÁC THỰC TÀI KHOẢN
        # -------------------------------------------------

        user = authenticate(

            request,

            username=username,

            password=password

        )


        # -------------------------------------------------
        # ĐĂNG NHẬP THÀNH CÔNG
        # -------------------------------------------------

        if user is not None:

            login(
                request,
                user
            )

            return redirect('home')


        # -------------------------------------------------
        # ĐĂNG NHẬP THẤT BẠI
        # -------------------------------------------------

        return render(
            request,
            'login.html',
            {
                'error':
                    'Tên đăng nhập hoặc mật khẩu không đúng!'
            }
        )


    # -----------------------------------------------------
    # HIỂN THỊ LOGIN
    # -----------------------------------------------------

    return render(
        request,
        'login.html'
    )


# =========================================================
# ĐĂNG XUẤT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect('home')

@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.username,
        }
    )

    return render(
        request,
        'profile.html',
        {
            'profile': profile
        }
    )

@login_required 
def profile(request): 
 
    profile, created = Profile.objects.get_or_create( 
        user=request.user, 
        defaults={ 
            'full_name': request.user.username, 
        } 
    ) 
 
    return render( 
        request, 
        'profile.html', 
        { 
            'profile': profile 
        } 
    )


# =========================================================
# THÔNG TIN KHÁCH HÀNG
# =========================================================

@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.username,
        }
    )

    return render(
        request,
        'profile.html',
        {
            'profile': profile
        }
    )


# =========================================================
# CHỈNH SỬA THÔNG TIN KHÁCH HÀNG
# =========================================================

@login_required
def profile_edit(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.username,
        }
    )

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():

            form.save()

            return redirect('profile')

    else:

        form = ProfileForm(
            instance=profile,
            user=request.user
        )

    return render(
        request,
        'profile_edit.html',
        {
            'profile': profile,
            'form': form
        }
    )


@login_required(login_url='login')
def payment_qr(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )
    bank_id = 'MB'
    account_no = '0123456789'
    account_name = 'MUSICSTORE'
    transfer_content = f'MUSICSTORE DH{order.id}'
    qr_url = (
        f'https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png'
        f'?amount={int(order.total)}&addInfo={transfer_content}'
        f'&accountName={account_name}'
    )

    return render(
        request,
        'payment_qr.html',
        {
            'order': order,
            'total': order.total,
            'qr_url': qr_url,
            'bank_id': bank_id,
            'account_no': account_no,
            'account_name': account_name,
            'transfer_content': transfer_content,
        }
    )
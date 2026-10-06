from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


# =========================================================
# FORM ĐĂNG KÝ
# =========================================================

class RegisterForm(UserCreationForm):

    full_name = forms.CharField(
        label='Họ và tên',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ và tên'
        })
    )

    date_of_birth = forms.DateField(
        label='Ngày sinh',
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        input_formats=['%Y-%m-%d']
    )

    username = forms.CharField(
        label='Tên đăng nhập',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập'
        })
    )

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email'
        })
    )

    password1 = forms.CharField(
        label='Mật khẩu',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu'
        })
    )

    password2 = forms.CharField(
        label='Nhập lại mật khẩu',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })
    )

    avatar = forms.ImageField(
        label='Ảnh đại diện',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

    # -----------------------------------------------------
    # KIỂM TRA USERNAME
    # -----------------------------------------------------

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                'Tên đăng nhập này đã tồn tại!'
            )

        return username

    # -----------------------------------------------------
    # KIỂM TRA EMAIL
    # -----------------------------------------------------

    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                'Email này đã được sử dụng!'
            )

        return email


# =========================================================
# FORM CHỈNH SỬA THÔNG TIN KHÁCH HÀNG
# =========================================================

class ProfileForm(forms.ModelForm):

    # Email nằm trong bảng auth_user
    # Không nằm trong Profile
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email'
        })
    )

    class Meta:
        model = Profile

        fields = [
            'full_name',
            'date_of_birth',
            'phone',
            'avatar'
        ]

        labels = {
            'full_name': 'Họ và tên',
            'date_of_birth': 'Ngày sinh',
            'phone': 'Số điện thoại',
            'avatar': 'Ảnh đại diện'
        }

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập họ và tên'
            }),

            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại'
            }),

        }

    # -----------------------------------------------------
    # KHỞI TẠO FORM
    # -----------------------------------------------------

    def __init__(
        self,
        *args,
        user=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.user = user

        # Lấy email từ auth_user
        if user:
            self.fields['email'].initial = user.email

    # -----------------------------------------------------
    # KIỂM TRA EMAIL
    # -----------------------------------------------------

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if email and self.user:

            exists = User.objects.filter(
                email=email
            ).exclude(
                id=self.user.id
            ).exists()

            if exists:

                raise forms.ValidationError(
                    'Email này đã được sử dụng.'
                )

        return email

    # -----------------------------------------------------
    # LƯU PROFILE + EMAIL USER
    # -----------------------------------------------------

    def save(self, commit=True):

        # Lưu:
        # full_name
        # date_of_birth
        # phone
        # avatar

        profile = super().save(
            commit=commit
        )

        # Lưu email vào auth_user
        if self.user:

            self.user.email = (
                self.cleaned_data.get('email', '')
            )

            self.user.save()

        return profile
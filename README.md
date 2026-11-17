# MusicStore

Website bán nhạc cụ được xây dựng bằng Django. Ứng dụng có danh mục sản phẩm,
giỏ hàng, đặt hàng, tài khoản khách hàng và khu vực quản trị.

## Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ](#công-nghệ)
- [Cài đặt và chạy local](#cài-đặt-và-chạy-local)
- [Dữ liệu và cơ sở dữ liệu](#dữ-liệu-và-cơ-sở-dữ-liệu)
- [Các luồng sử dụng](#các-luồng-sử-dụng)
- [Vai trò và quản trị](#vai-trò-và-quản-trị)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Kiểm thử](#kiểm-thử)
- [Triển khai và bảo mật](#triển-khai-và-bảo-mật)
- [Ghi nhận](#ghi-nhận)

## Tính năng

### Khách hàng

- Xem danh sách sản phẩm, lọc theo danh mục và tìm kiếm theo tên hoặc danh
  mục.
- Xem thông tin chi tiết, giá, mô tả và số lượng còn trong kho.
- Thêm sản phẩm vào giỏ hàng; thay đổi số lượng hoặc xóa sản phẩm. Giỏ hàng
  được lưu trong session của trình duyệt.
- Đăng ký tài khoản với họ tên, ngày sinh, email, tên đăng nhập, mật khẩu và
  ảnh đại diện tùy chọn.
- Đăng nhập, đăng xuất, xem và cập nhật hồ sơ cá nhân.
- Đặt hàng sau khi đăng nhập, cung cấp thông tin nhận hàng và ghi chú.
- Chọn thanh toán khi nhận hàng (COD) hoặc xem mã QR chuyển khoản.
- Xem danh sách và chi tiết các đơn hàng thuộc tài khoản của mình.

### Quản trị

- Quản lý sản phẩm, tồn kho, đơn hàng, chi tiết đơn hàng, hồ sơ và tài khoản
  qua Django Admin.
- Tìm kiếm và lọc sản phẩm, khách hàng, đơn hàng; cập nhật trạng thái đơn hàng.
- Trạng thái đơn hàng: chờ xác nhận (`pending`), đã xác nhận (`confirmed`),
  đang giao (`shipping`), đã giao (`completed`) và đã hủy (`cancelled`).

## Công nghệ

- Python 3.14
- Django 6.1
- SQLite, sử dụng backend tùy chỉnh trong `config/db/backends/sqlite3/`
- Pillow 12.3.0 để xử lý trường ảnh đại diện
- Giao diện Django Templates, CSS và HTML

Các phiên bản trên là môi trường đã dùng để kiểm tra dự án. Repository hiện
chưa có `requirements.txt` hoặc tệp khóa dependency; khi tạo môi trường mới,
có thể cài đúng các phiên bản này bằng lệnh ở phần cài đặt bên dưới.

## Cài đặt và chạy local

Các lệnh sau dành cho Windows PowerShell, chạy từ thư mục gốc của dự án.

### 0. Tải mã nguồn

```powershell
git clone https://github.com/kiapham52-pixel/24CT1_NhatHuy_CNPM.git
Set-Location 24CT1_NhatHuy_CNPM
```

### 1. Chuẩn bị Python và môi trường ảo

Cài Python 3.14, sau đó tạo và kích hoạt môi trường ảo:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn kích hoạt script, có thể bỏ qua bước kích hoạt và gọi
trực tiếp Python trong `.venv` như các lệnh bên dưới.

### 2. Cài dependency

```powershell
python -m pip install --upgrade pip
python -m pip install Django==6.1 Pillow==12.3.0
```

### 3. Cấu hình khóa bí mật

Trong PowerShell hiện tại, đặt khóa dùng cho môi trường phát triển:

```powershell
$env:DJANGO_SECRET_KEY = "thay-bang-chuoi-bi-mat-rieng-cua-ban"
```

Không đưa khóa bí mật thật vào Git. Nếu biến này chưa được đặt, cấu hình hiện
tại sử dụng một khóa dự phòng chỉ dành cho phát triển.

### 4. Tạo cơ sở dữ liệu và tài khoản quản trị

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Lệnh `migrate` tạo `MusicStoreDB.sqlite3` và áp dụng các migration nếu file
chưa tồn tại. Lệnh `createsuperuser` tạo tài khoản quản trị Django.

### 5. Khởi chạy

```powershell
python manage.py runserver
```

Mở [http://127.0.0.1:8000/](http://127.0.0.1:8000/) để dùng cửa hàng và
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) để vào Django
Admin. Máy chủ phát triển chỉ phù hợp cho local.

## Dữ liệu và cơ sở dữ liệu

- Cấu hình mặc định lưu dữ liệu tại `MusicStoreDB.sqlite3` ở thư mục gốc.
- `db.sample.sqlite3` là bản dữ liệu mẫu đã được làm sạch, phù hợp để xem thử
  dữ liệu demo. Chỉ sao chép bản mẫu nếu `MusicStoreDB.sqlite3` chưa tồn tại
  hoặc bạn đã sao lưu file hiện tại; lệnh sao chép sẽ ghi đè database đích.
  Sau đó chạy migration:

  ```powershell
  Copy-Item db.sample.sqlite3 MusicStoreDB.sqlite3
  python manage.py migrate
  ```

- `db.sqlite3` là tên database cũ; cấu hình hiện tại không tự động đọc file
  này. Nếu cần chuyển dữ liệu từ database cũ, trước tiên bảo đảm
  `MusicStoreDB.sqlite3` chưa tồn tại (hoặc đã được sao lưu), rồi tạo bản sao
  nhất quán bằng SQLite backup API:

  ```powershell
  python -c "import sqlite3; src=sqlite3.connect('db.sqlite3'); dst=sqlite3.connect('MusicStoreDB.sqlite3'); src.backup(dst); dst.close(); src.close()"
  python manage.py migrate
  ```

  Xác minh ứng dụng và dữ liệu trước khi xóa hoặc thay thế bản gốc.
- Database local, các file SQLite journal và thư mục `media/` được Git bỏ qua.
  Ảnh đại diện tải lên nằm trong `media/avatars/`; hãy lưu trữ và sao lưu
  riêng nếu cần giữ lại.
- Mọi thay đổi schema cần có migration. Sau khi lấy code mới, chạy
  `python manage.py migrate`.

### Mô hình dữ liệu

- **Product**: tên, danh mục dạng văn bản, giá, URL hình ảnh, mô tả và số
  lượng tồn kho.
- **Order**: tài khoản (có thể rỗng với dữ liệu đơn hàng cũ), thông tin nhận
  hàng, ghi chú, tổng tiền, trạng thái và thời điểm tạo.
- **OrderItem**: sản phẩm, số lượng và giá tại thời điểm đặt hàng; sản phẩm
  được giữ lại nếu đã xuất hiện trong đơn.
- **Profile**: họ tên, ngày sinh, số điện thoại và ảnh đại diện; liên kết một
  - một với tài khoản Django.
- Django **User**, **Group** và **Permission**: thông tin đăng nhập và phân
  quyền.

Danh mục hiện được lưu trực tiếp trên `Product.category`, không có bảng danh
mục riêng.

## Các luồng sử dụng

### Mua hàng

1. Duyệt hoặc tìm kiếm sản phẩm, mở trang chi tiết và thêm sản phẩm vào giỏ.
2. Đăng nhập hoặc đăng ký; checkout yêu cầu người dùng đã đăng nhập.
3. Nhập tên, số điện thoại, địa chỉ nhận hàng và ghi chú tùy chọn.
4. Chọn COD hoặc chuyển khoản. Khi tạo đơn, ứng dụng kiểm tra tồn kho trong
   transaction, lưu đơn và chi tiết đơn, sau đó trừ số lượng trong kho.
5. Theo dõi đơn trong mục đơn hàng của tài khoản.

Đơn mới được tạo ở trạng thái `pending`. Nếu chọn COD, trang xác nhận đơn sẽ
được hiển thị. Nếu chọn chuyển khoản, ứng dụng hiển thị QR VietQR với số tiền
và nội dung chuyển khoản gắn với mã đơn hàng.

**Lưu ý thanh toán:** cấu hình ngân hàng hiện nằm trực tiếp trong
`store/views.py` và đang dùng dữ liệu mẫu (`MB`, `0123456789`, `MUSICSTORE`).
Hãy thay bằng thông tin tài khoản thật trước khi sử dụng. Ứng dụng hiện chỉ
tạo và hiển thị mã QR; không tích hợp cổng thanh toán, không tự xác nhận tiền
đã vào tài khoản và không tự cập nhật trạng thái đơn sau thanh toán. Không
dùng thông tin mẫu để nhận tiền thật.

### Các URL chính

| URL | Mục đích | Yêu cầu đăng nhập |
| --- | --- | --- |
| `/` và `/products/` | Danh sách, tìm kiếm và lọc sản phẩm | Không |
| `/product/<id>/` | Chi tiết sản phẩm | Không |
| `/cart/` | Xem giỏ hàng | Không |
| `/checkout/` | Tạo đơn hàng | Có |
| `/orders/` | Danh sách đơn của tài khoản hiện tại | Có |
| `/orders/<id>/` | Chi tiết đơn hàng của chủ đơn | Có |
| `/orders/payment/<id>/` | QR chuyển khoản của chủ đơn | Có |
| `/register/`, `/login/` | Đăng ký, đăng nhập | Không |
| `/logout/` | Đăng xuất | Không |
| `/profile/`, `/profile/edit/` | Xem và sửa hồ sơ | Có |
| `/admin/` | Django Admin | Có quyền quản trị |

Tìm kiếm trên trang sản phẩm dùng tham số `q`; lọc danh mục dùng `category`,
ví dụ `/?q=guitar&category=Guitar`.

## Vai trò và quản trị

Migration tạo hai nhóm Django:

- **CUSTOMER**: tài khoản đăng ký mới được thêm vào nhóm này và không có quyền
  quản trị.
- **ADMIN**: nhóm nhân viên quản lý cửa hàng, được cấp quyền trên tài khoản,
  sản phẩm, đơn hàng, chi tiết đơn và hồ sơ.

Truy cập Django Admin cần `is_staff=True` (hoặc superuser). Nhân viên thuộc
nhóm ADMIN không thể tự nâng tài khoản thành staff/superuser, không thể quản
lý tài khoản staff khác và không thể xóa tài khoản; việc cấp quyền quản trị
cao hơn dành cho superuser. Tạo superuser bằng `createsuperuser`, sau đó dùng
tài khoản này để quản lý quyền nhân viên.

## Cấu trúc dự án

```text
config/                 Cấu hình Django, URL và SQLite backend tùy chỉnh
store/                  Ứng dụng cửa hàng
  migrations/           Migration database
  static/store/         CSS và hình ảnh tĩnh
templates/              Giao diện Django Templates
media/                  File tải lên (không đưa lên Git)
manage.py               Django command-line utility
db.sample.sqlite3       Database demo đã làm sạch
```

## Kiểm thử

Chạy toàn bộ test:

```powershell
python manage.py test
```

Các test hiện có kiểm tra đăng ký và phân quyền CUSTOMER, quyền quản trị của
ADMIN, giới hạn truy cập đơn hàng theo chủ sở hữu và các khu vực Django Admin.

## Triển khai và bảo mật

Cấu hình đang có trong repository dành cho local development, không an toàn
để đưa trực tiếp lên Internet:

- `DEBUG = True`: trang lỗi có thể tiết lộ thông tin chẩn đoán.
- `ALLOWED_HOSTS = ['*']`: chấp nhận mọi hostname.
- `SECRET_KEY` có khóa dự phòng nếu `DJANGO_SECRET_KEY` chưa được đặt.

Đặt `DJANGO_SECRET_KEY` thay khóa dự phòng nhưng **không** tắt DEBUG hay giới
hạn ALLOWED_HOSTS. Trước khi triển khai, dùng cấu hình production riêng hoặc
cập nhật `config/settings.py`: tắt debug, chỉ cho phép đúng hostname, yêu cầu
khóa bí mật mạnh không có fallback, bật HTTPS và cấu hình database, static
files, uploads, backup, logging và email phù hợp với môi trường vận hành.
Không dùng máy chủ `runserver` cho production. Tham khảo
[Django deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/).

## Ghi nhận

Logo tại `store/static/store/images/logo.png` là logo nguyên bản của Trường
Đại học Kiến trúc Đà Nẵng, do trường tạo và lấy từ
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Logo_dhktdn.png).
Logo được cấp phép theo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

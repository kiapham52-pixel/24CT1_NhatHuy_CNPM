# 24CT1 Nhat Huy

## Run locally

Set `DJANGO_SECRET_KEY` to a private value before starting Django. Do not commit
the value to Git.

```powershell
$env:DJANGO_SECRET_KEY = "your-private-secret-key"
.\venv\Scripts\python.exe manage.py runserver
```

`db.sample.sqlite3` is a sanitized demo snapshot. Your local `db.sqlite3` and
uploaded media are intentionally excluded from Git.

## Database and user roles

The application uses Django ORM with SQLite at `MusicStoreDB.sqlite3`. When
upgrading from an existing `db.sqlite3`, create the new file with SQLite's
online backup API before switching databases; keep the original file until the
copy and application have been verified.

Django's built-in `User`, `Group`, and `Permission` models provide access
control. The `ADMIN` group has product, order, profile, and user-management
permissions; admin-site access also requires Django's `is_staff` flag.
Self-registered accounts are assigned to `CUSTOMER` and cannot set staff or
superuser flags. Promote staff accounts only through an existing superuser.
Product categories are stored on `Product`; there is no separate category
table.

After switching or restoring a database, run:

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

## Logo attribution

The logo at `store/static/store/images/logo.png` is the unmodified logo of
Trường Đại học Kiến trúc Đà Nẵng, authored by the university and sourced from
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Logo_dhktdn.png).
It is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

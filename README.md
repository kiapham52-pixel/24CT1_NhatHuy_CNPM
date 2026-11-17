# 24CT1 Nhat Huy

## Run locally

For local development, set `DJANGO_SECRET_KEY` to a private value before
starting Django. Do not commit the value to Git. If it is not set,
`config/settings.py` uses a development-only fallback key.

```powershell
$env:DJANGO_SECRET_KEY = "your-private-secret-key"
.\venv\Scripts\python.exe manage.py runserver
```

`db.sample.sqlite3` is a sanitized demo snapshot. Your local `db.sqlite3` and
uploaded media are intentionally excluded from Git.

## Deployment and security

The settings currently checked into this project are for local development,
not for a public production deployment:

- `DEBUG` is enabled, which can expose diagnostic details if an error occurs.
- `ALLOWED_HOSTS` accepts every host name.
- A fallback `SECRET_KEY` is used when `DJANGO_SECRET_KEY` is missing.

Setting `DJANGO_SECRET_KEY` replaces the fallback key, but does **not** disable
`DEBUG` or restrict `ALLOWED_HOSTS`. Before deploying, update
`config/settings.py` (or use a deployment-specific settings module) to disable
debug mode, set `ALLOWED_HOSTS` to the exact host names serving the app, and
require a strong, private `DJANGO_SECRET_KEY` with no fallback. Keep secrets
outside the repository. Also configure HTTPS and review Django's deployment
checklist for the chosen hosting environment:
[Django deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/).

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

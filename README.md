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

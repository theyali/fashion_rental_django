# Production deployment

The repository now has two Docker modes:

- `docker-compose.yml` — local development with Django `runserver` and source bind mount.
- `docker-compose.prod.yml` — PostgreSQL + Gunicorn + Nginx with persistent static/media volumes.

## 1. Prepare environment

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` and set at least:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `SITE_URL`
- contact details
- SMTP credentials

`.env.prod` is ignored by git.

## 2. First production start

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

Check services:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f web nginx
```

Health endpoint:

```text
/healthz/
```

SEO endpoints:

```text
/sitemap.xml
/robots.txt
```

## 3. Demo/import seed

`SEED_DEMO=1` imports the content from `/dresses` and prepares demo media. After the initial import, set `SEED_DEMO=0` if catalog content will be managed manually through Django Admin and should not be refreshed on every container restart.

## 4. HTTPS

The included Nginx config listens on HTTP port 80. Put HTTPS either directly on Nginx or in front of it using a reverse proxy/load balancer. After HTTPS is working, enable:

```env
SECURE_SSL_REDIRECT=1
SECURE_COOKIES=1
SECURE_HSTS_SECONDS=31536000
```

Do not enable HSTS before HTTPS is confirmed working for the real domain.

## 5. Email notifications

Production can use SMTP through `.env.prod`. New contact requests and bookings are stored in PostgreSQL first; email notifications are supplementary and do not replace database records.

## Useful commands

```bash
# Django checks
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py check --deploy

# Create admin user
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py createsuperuser

# Migrations
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate

# Restart web/nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod restart web nginx
```

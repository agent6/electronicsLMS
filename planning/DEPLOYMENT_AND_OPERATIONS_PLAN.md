<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Deployment and Operations Plan

## Deployment Target

ObsoleteHQ is planned as a Docker Compose stack deployed through Portainer on an Ubuntu server. Cloudflare Tunnel and DNS are external operations handled outside this project.

## Stack Services

- `django-web`: Django application server.
- `postgres`: PostgreSQL database.
- Optional future worker only if background work becomes necessary.

No Compose file is created in this planning package.

## Persistent Data

- PostgreSQL volume for database data.
- Local media volume reserved for future uploads and operational files.
- Static files collected by the web image or served through the chosen production static strategy.

## Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` or database connection fields
- `BREVO_API_KEY`
- `DEFAULT_FROM_EMAIL`
- `STATIC_ROOT`
- `MEDIA_ROOT`

## Backups

Plan daily PostgreSQL backups with retention and a documented restore test. A backup plan is incomplete until restore has been tested on a non-production environment.

## Local and Production Environments

- Local: developer environment with Django, PostgreSQL, and generated test data.
- Production: Portainer stack on Ubuntu, reached through externally managed Cloudflare Tunnel.

## Health and Logging

- Health endpoint for web service.
- Database connectivity check.
- Static/media path check.
- Email delivery status from Brevo events.
- Structured application logs.
- Error monitoring can be added after core operations are stable.

## Upgrade and Rollback

Use tagged images, database backup before migrations, documented deploy steps, and a rollback path to the previous image plus database restore when schema changes require it.

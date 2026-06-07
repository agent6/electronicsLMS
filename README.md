# ObsoleteHQ

ObsoleteHQ is a Django, PostgreSQL, Tailwind CSS, and HTMX learning platform for teen electronics projects. The app is server-rendered, deployable as a Docker Compose stack in Portainer, and ready for the first real lesson to be added through the admin/content system.

## Local Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm install
npm run build:css
python manage.py migrate
python manage.py seed_obsoletehq
python manage.py runserver 4173
```

Open `http://localhost:4173/`. If no user exists, the app redirects to `/setup/` to create the first admin account.

## First Run

1. Open the site.
2. Complete `/setup/` to create the first superuser.
3. Run `python manage.py seed_obsoletehq` if structural data is not already seeded.
4. Open `/studio/` or `/admin/`.
5. Add a Learning Experience with at least one published section.
6. Set status to `Published`.
7. View it from `/tutorials/` or `/learn/a-la-carte/`.

## Content Author Workflow

- Create kits, components, tracks, safety warnings, and Core Run weeks first.
- Create a Learning Experience with code, title, track, content type, difficulty, summary, hook, estimated time, and student outcome.
- Add ordered sections.
- Keep status `Draft`, `Review`, `Hidden`, or `Retired` until the lesson is complete.
- Only `Published` learning experiences appear in student-facing pages.
- Draft/hidden content does not appear in nav, filters, dashboards, or lesson cards.

## Styling System

- Source CSS: `static/src/styles.css`
- Compiled CSS: `static/css/app.css`
- Tailwind config: `tailwind.config.js`
- No Tailwind CDN.
- No inline CSS or `<style>` blocks in templates.
- Shared button, card, empty-state, form, nav, and layout patterns live in the Tailwind component layer.

## Docker Compose / Portainer

1. Copy `.env.example` to `.env` and set strong secrets. `DJANGO_SECRET_KEY` is required when `DJANGO_DEBUG=false`; the stack will fail fast if it is missing.
2. In Portainer, create a stack from `docker-compose.yml`.
3. Deploy the stack.
4. Open the public URL routed through your external Cloudflare Tunnel.
5. Complete `/setup/`.

The web container runs `python manage.py migrate --noinput` and `python manage.py seed_obsoletehq` on startup by default. To disable either behavior, set `DJANGO_RUN_MIGRATIONS=false` or `DJANGO_SEED_ON_STARTUP=false` in the stack environment.

Cloudflare Tunnel and DNS are intentionally outside this project.

## Backup / Restore Notes

Back up the `postgres_data` volume daily. A practical backup command from the Postgres container is:

```bash
pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > obsoletehq-backup.sql
```

Test restores before relying on backups.

## Manual QA Checklist

- `/setup/` appears only before users exist.
- Setup creates and logs in the first admin.
- Setup locks after a superuser exists.
- Homepage, safety, parts, debug, tutorials, Core Run, A la Carte, login, logout, dashboard, and Dev Log pages load.
- Dashboard requires authentication.
- Draft learning experiences remain hidden.
- Published learning experiences can be completed.
- Completion creates progress and XP.
- Dev Logs are private to the owner.
- Navigation links resolve to real routes.
- Mobile views have no horizontal overflow.

## Known Limitations

- Public gallery and public student profiles are not active.
- Badge awarding is modeled but intentionally minimal until criteria are implemented.
- Evidence uploads are modeled but not exposed in the student UI.
- The custom studio is a polished operational summary; detailed content editing uses Django admin.

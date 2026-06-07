<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Information Architecture

## Public Routes

- `/`: homepage with student-focused positioning and Start Learning call to action.
- `/tutorials`: published tutorial index and preview browsing.
- `/tutorials/[slug]`: published tutorial page or public preview, depending on account state.
- `/parts`: published parts library.
- `/debug`: symptom-based debugging help.
- `/safety`: hardware safety center.
- `/login`: login.
- `/signup`: account creation.

## Logged-In Routes

- `/learn`: student dashboard and resume point.
- `/learn/core-run`: recommended 21-stop Core Run map showing published available stops only.
- `/learn/core-run/stop-[number]`: stop page if all required referenced lessons are published.
- `/learn/a-la-carte`: searchable library of published tutorials.
- `/profile`: account and display name.
- `/profile/progress`: progress, XP, badges, and momentum.
- `/profile/project-passport`: completed skill areas and Core Run stops.
- `/dev-log`: private Dev Logs.
- `/projects`: student's project writeups.
- `/projects/[slug]`: public text project writeup.

## Admin Routes

- `/admin`: custom operations dashboard.
- `/admin/content`: tutorials, tracks, parts, references, safety notes, and publish controls.
- `/admin/users`: account state and verification status.
- `/admin/projects`: public project visibility data.
- `/admin/analytics`: privacy-first product events.
- `/admin/email`: Brevo delivery status.
- `/admin/health`: app, database, static, media, and job health.

## Navigation Rules

- Student navigation includes only routes with complete behavior.
- Hidden tutorials do not appear in search, next links, dashboard cards, or library filters.
- Buttons only appear when the action works.
- Roadmap pages for unpublished content are not public product pages.

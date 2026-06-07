<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Tech Stack and Architecture

## Stack Fit

Django fits the product because ObsoleteHQ is a server-rendered learning app with accounts, content publishing, admin operations, progress tracking, and durable relational data. PostgreSQL fits the structured curriculum and event data. Tailwind CSS supports a consistent visual system. HTMX adds focused interactivity without turning the app into a heavy single-page application.

## High-Level Architecture

- Django web app serves public, student, and admin pages.
- PostgreSQL stores users, content, progress, projects, events, and operations data.
- Tailwind defines design tokens, layout utilities, and responsive components.
- HTMX handles incremental updates for completion, Dev Log saves, filters, XP feedback, badges, project edits, and admin publish checks.
- Brevo sends verification, password reset, and essential account emails.

## Django App Breakdown

- `accounts`: authentication, verification, display names, roles.
- `curriculum`: tracks, tutorials, steps, parts, safety, references.
- `learning`: progress, checkpoints, Dev Logs, XP, badges, momentum, passport.
- `projects`: public text project writeups.
- `operations`: custom admin dashboards, product events, email status, health.
- `core`: shared navigation, route visibility, design primitives, error pages.

## Data Strategy

Use relational tables for curriculum, progress, and project data. Use append-only event records for XP, momentum, product analytics, email events, and publish audits. Avoid storing unnecessary personal data.

## HTMX Strategy

Use HTMX for small, resilient interactions:

- Mark lesson complete.
- Save Dev Log.
- Update progress card.
- Filter tutorials.
- Show XP/badge success state.
- Edit project writeup sections.
- Preview admin publish checks.

Every HTMX interaction should have a full-page fallback or a safe reload path.

## Security

- CSRF on all state-changing forms.
- Secure session cookies in production.
- Email verification before public publishing.
- Role checks for admin routes.
- No secrets in public GitHub.
- Environment variables for Django secret, database, Brevo, allowed hosts, CSRF origins, static/media settings.

## Accessibility and Performance

Use semantic HTML, WCAG AA contrast, keyboard navigation, visible focus states, responsive layouts, reduced-motion support, query prefetching where needed, and cached published content lists after implementation.

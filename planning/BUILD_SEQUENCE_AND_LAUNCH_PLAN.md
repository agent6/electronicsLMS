<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Build Sequence and Launch Plan

## Sequence Principle

Build the complete product in slices, but expose only finished behavior. The product UI should never show unauthored tutorials, incomplete filters, dead buttons, empty active routes, or fake progress.

## Sequence 1: Foundation

- Public homepage.
- Signup/login/logout.
- Username, private email, display name.
- Brevo verification and password reset.
- Dashboard shell with only working cards.
- Custom admin base.

## Sequence 2: Content System

- Tracks, tutorials, parts, safety warnings, references, and steps.
- Draft/published content states.
- Student tutorial reading page.
- Admin preview and publish checks.
- Published-only tutorial index.

## Sequence 3: Progress

- Tutorial checkpoint self-check.
- Private Dev Logs.
- Progress events.
- Lightweight XP.
- Earnable badges.
- Meaningful-session momentum.

## Sequence 4: Core Run and A la Carte

- Recommended Core Run map using published stops only.
- A la Carte filters for published tutorials only.
- Parts library and debugging center.
- Project passport for real completed skill areas.

## Sequence 5: Projects

- Public text project writeups.
- Email verification gate.
- Display-name attribution.
- Student edit flow.

## Sequence 6: Operations and Hardening

- Admin operations dashboard.
- Product event metrics.
- Email delivery visibility.
- Health checks.
- Backup and restore documentation.
- Accessibility and responsive QA.

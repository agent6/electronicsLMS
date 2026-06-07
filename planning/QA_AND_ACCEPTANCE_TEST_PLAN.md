<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# QA and Acceptance Test Plan

## Manual QA

- Homepage CTA reaches signup.
- Signup, login, logout, verification email, and password reset work.
- Dashboard shows only real progress and published recommendations.
- Tutorial completion creates checkpoint, private Dev Log, XP event, and progress update.
- Hidden tutorials are absent from all student paths.
- A la Carte filters return only published tutorials.
- Public project publishing requires verified email.
- Public project page shows display name only.
- Student can edit project writeup.
- Custom admin can create, preview, and publish content.

## Mobile QA

- No horizontal scrolling.
- Tutorial text is readable.
- Parts lists, safety notes, filters, forms, and project editing work by touch.
- Buttons and inputs have sufficient target size.

## Desktop QA

- Dashboard, tutorial pages, library filters, project pages, and admin tables use space efficiently.
- Keyboard navigation works.
- Focus states are visible.

## Accessibility QA

- Semantic headings.
- Labels for inputs.
- Contrast meets WCAG AA.
- Screen-reader status messages for saves, errors, and completion.
- Reduced-motion setting respected.

## Operations QA

- Portainer stack deploys.
- App reaches database.
- Static files load.
- Media volume mounts.
- Brevo transactional email sends.
- Daily backup runs.
- Restore process is documented and tested.
- Health endpoint reports app and database status.

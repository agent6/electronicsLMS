<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Feature Completion Policy

## Complete

A feature is complete when it is implemented end to end, tested on mobile and desktop, has useful empty/loading/error states, has permission handling, has no dead links, and can be operated without hidden manual steps.

## Not Ready

A feature is not ready if it has empty planned pages, dead buttons, missing routes, incomplete data, fake progress, fake achievements, broken filters, or unauthored tutorial content.

## Visibility Rules

- Hidden content is absent from student UI.
- Draft tutorials do not appear in search, filters, Core Run, A la Carte, next suggestions, or progress prompts.
- Active navigation links exist only for complete routes.
- Roadmap content is internal planning, not public UI.
- Empty pages are not acceptable active features.

## Publish Checks

Before enabling a feature:

- Happy path works.
- Empty state is useful.
- Validation is clear.
- Permissions are correct.
- Mobile and desktop layouts work.
- Accessibility basics pass.
- Links work.
- Error states are understandable.
- No fake data is required to make the page look complete.

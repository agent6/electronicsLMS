<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# UX Flows

## First Learning Flow

1. Student lands on `/`.
2. Student chooses Start Learning.
3. Student creates account with username, email, password, and display name.
4. Student lands on `/learn`.
5. Student sees first published setup tutorial.
6. Student completes setup checkpoint.
7. Student writes a short private Dev Log.
8. Dashboard updates progress, XP, and next recommended published tutorial.
9. Student starts blink when published and available.

## Browse Published Content

1. Student opens A la Carte library.
2. Filters show only published tutorials.
3. Student filters by part, skill, difficulty, time, and project type.
4. Tutorial cards show required parts, expected result, and prerequisite hints.
5. Student can open any published tutorial without artificial locks.

## Return After Break

1. Student logs in.
2. Dashboard shows resume card, latest Dev Log, and next recommended published lesson.
3. Momentum copy recognizes the return without penalty.
4. Student continues any published lesson or edits a project writeup.

## Publish Project Writeup

1. Student opens Projects.
2. Student starts a text project writeup.
3. If email is not verified, the app requires verification first.
4. Student writes title, summary, parts, behavior, debugging notes, and next improvement.
5. Project page publishes with display name only.
6. Student can edit the writeup later.

## Admin Publish Flow

1. Admin creates or edits tutorial content in custom admin.
2. Admin fills required metadata, safety notes, references, and visibility state.
3. Admin previews the student page.
4. Admin runs publish checks for links, missing sections, route behavior, and next links.
5. Admin publishes only when the page is complete.

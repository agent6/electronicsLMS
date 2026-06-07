<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Product Requirements Document

## Vision

ObsoleteHQ helps teen students turn intimidating electronics into visible, working projects. The product starts with one blinking LED and grows toward independent hardware inventions using MicroPython and Raspberry Pi Pico 2 W.

## Problem

Beginner hardware learning often fails because students face too many unknowns at once: code, breadboards, parts, wiring, safety, errors, and unclear progress. ObsoleteHQ reduces that load by giving students a clear path, small wins, private Dev Logs, and public text project writeups when they are ready to show what they built.

## Target Users

- Students ages 13-17 with no electronics experience.
- Students with some coding experience who want real-world hardware projects.
- Fast-moving students who want to choose projects freely.
- Students with limited kit access who need self-paced progress that does not punish gaps.
- Internal admins and content operators who publish curriculum and operate the site.

## Jobs To Be Done

- Learn how to set up a Pico 2 W and run MicroPython safely.
- Build visible, audible, sensing, moving, and connected projects.
- Understand each new part by first reading raw values or making the simplest possible output.
- Keep progress through private Dev Logs.
- Publish text project writeups without revealing personal details.
- Browse only content that is complete enough to use.
- Return after a break without losing identity, progress, or momentum.

## Success Metrics

- Account creation to first completed setup tutorial.
- First setup completion to first blink completion.
- Percent of students writing at least one Dev Log.
- Percent of students completing three or more published tutorials.
- Percent of students returning after seven or more days away.
- Public writeups created after email verification.
- Published content with zero dead links or broken active UI.
- Admin time required to publish a new lesson cleanly.

## Product Requirements

- Public homepage explains ObsoleteHQ and routes students to start learning.
- Public curriculum previews show what is available without exposing unfinished pages.
- Signup uses username, private email, password, and separate display name.
- Email verification is required before public publishing.
- Tutorials are server-rendered, mobile-first, and readable on small screens.
- Completion uses self-check plus a private Dev Log entry.
- No quizzes are required for progress.
- Public project writeups are text-only, public by default, editable by the student, and tied to display name.
- The app never asks for full name, school, address, precise location, phone number, or social handle.
- Published tutorials appear in navigation and search; hidden tutorials do not.
- Admins have a clean custom operations dashboard for content, users, public projects, analytics basics, email status, and health signals.

## Constraints

- Stack: Django, PostgreSQL, Tailwind CSS, HTMX.
- Packaging: Docker Compose deployed as a Portainer stack on Ubuntu.
- Cloudflare Tunnel is managed outside this project.
- Brevo handles transactional email.
- Curriculum is CC BY 4.0.
- Application code is planned for public GitHub, default software license MIT unless changed.
- No application implementation belongs in this planning package.

## Risks

- Public-by-default student project text without platform review creates privacy and abuse risk.
- No automated personal-information scanning means copy and field design must strongly avoid collecting sensitive data.
- Text-only projects are safer than media uploads but less visual for electronics work.
- Public GitHub from day one requires discipline around secrets, fixtures, and private operational notes.

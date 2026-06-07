<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Implementation Backlog

## Epic: Product Foundation

- Story: Visitor understands ObsoleteHQ from homepage.
  Acceptance: homepage has student-focused positioning, Start Learning CTA, kit/parts explanation, safety posture, and no dead links.
- Story: Student can create an account.
  Acceptance: username, private email, password, display name, login, logout, and verification email via Brevo work end to end.
- Story: Student can resume learning.
  Acceptance: dashboard shows current progress, latest Dev Log, and next published recommendation.

## Epic: Curriculum Delivery

- Story: Admin can author and publish tutorials.
  Acceptance: custom admin supports draft/published state, metadata, steps, references, safety notes, and preview.
- Story: Student can read a published tutorial.
  Acceptance: mobile and desktop layouts work, required parts are clear, and completion checkpoint is available.
- Story: Hidden tutorials stay hidden.
  Acceptance: hidden content is absent from navigation, search, filters, next links, and dashboards.

## Epic: Progress and Motivation

- Story: Student completes a tutorial.
  Acceptance: self-check plus private Dev Log creates progress event, XP event, and dashboard update.
- Story: Student earns badges.
  Acceptance: only badges tied to available actions appear and can be earned.
- Story: Momentum rewards meaningful sessions.
  Acceptance: progress does not punish missed days.

## Epic: Projects

- Story: Student writes a public text project.
  Acceptance: verified email is required, writeup is public with display name only, and student can edit it.
- Story: Student manages private Dev Logs.
  Acceptance: logs are private, searchable by student, and linked to lessons/projects.

## Epic: Admin Operations

- Story: Admin monitors content and operations.
  Acceptance: custom admin shows users, content state, public project list, product events, Brevo email status, and health checks.

## Epic: Deployment

- Story: Deploy as Portainer stack.
  Acceptance: Django, PostgreSQL, static handling, local media volume, backups, environment variables, and health checks are planned before implementation.

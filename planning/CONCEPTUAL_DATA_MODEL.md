<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Conceptual Data Model

## Identity and Roles

- User: username, private email, password hash, email verification state, display name, account status, timestamps.
- Role: student or admin.
- Profile: public display name, optional short bio constrained to non-personal project interests, privacy flags.

## Curriculum Entities

- Kit has many Components.
- Component belongs to zero or more Kits.
- Track has many Tutorials.
- Tutorial has many TutorialSteps, Components, Skills, SafetyWarnings, TroubleshootingItems, ExternalReferences, and Challenges.
- CoreRun has many CoreRunStops.
- CoreRunStop references one or more anchor Tutorials.

## Progress Entities

- User has many ProgressEvents.
- User has many DevLogEntries.
- User has many XPEvents.
- User earns many Badges through BadgeAward records.
- User has many MomentumEvents.
- User has many ProjectPassportStamps.
- CoreRunProgress records completed stops and latest recommended stop.

## Project Entities

- Project belongs to User.
- Project has title, slug, summary, parts used, behavior, debugging notes, next improvement, public state, and timestamps.
- Project is text-only in the planned product.
- Project attribution uses display name only.

## Admin and Operations Entities

- ContentAuditEvent records publish state changes.
- EmailEvent records Brevo transactional email status.
- ProductEvent records privacy-first analytics events.
- HealthCheckSnapshot records operational status.

## Privacy Considerations

Private email is never shown publicly. The schema should avoid full name, school, location, phone, social handles, and precise personal identifiers.

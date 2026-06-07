<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Content Model

## Core Content Types

- Track: named curriculum area with ordering and description.
- Tutorial: publishable lesson with metadata, required parts, safety notes, steps, references, and completion checkpoint.
- TutorialStep: ordered section within a tutorial.
- Component: reusable hardware part with pins, power, signal type, warnings, and related tutorials.
- Kit: recommended source bundle for parts, never a hard purchase lock.
- Skill: learning capability such as GPIO output, analog input, PWM, I2C, wireless, or project structure.
- CoreRun: recommended 21-stop path.
- CoreRunStop: group of anchor tutorials for a stop.
- Challenge: remix prompt tied to a tutorial.
- TroubleshootingItem: symptom, likely causes, checks, and fixes.
- SafetyWarning: contextual warning attached to parts, lessons, or project types.
- ExternalReference: source link with title, source name, and reason for reference.

## User-Generated Content Types

- DevLogEntry: private reflection attached to lesson or project progress.
- Project: public text writeup after email verification.
- ProgressEvent: record of meaningful student action.
- Badge: earnable milestone tied to real behavior.
- XPEvent: lightweight points ledger.
- MomentumEvent: meaningful-session record.
- ProjectPassportStamp: completed skill or Core Run stop.

## Publishing State

Content uses simple draft and published states. Draft content is hidden from all student-facing navigation. Published content must pass completion checks before appearing.

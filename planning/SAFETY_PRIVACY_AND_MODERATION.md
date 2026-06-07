<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Safety, Privacy, and Moderation

## Hardware Safety

Every hardware lesson must include warnings when relevant:

- Pico 2 W GPIO uses 3.3V logic.
- Do not feed 5V signals into Pico GPIO.
- Do not power motors, pumps, relays, or high-current loads directly from GPIO pins.
- Use motor drivers, transistors, relay modules, diodes, and external power appropriately.
- Avoid mains voltage entirely.
- Relay work is low-voltage DC only.
- LiPo charging requires strong caution.
- Laser modules require eye safety warnings.
- Flame sensor lessons must not encourage unsafe fire activity.
- Heartbeat sensors are educational only and not medical devices.
- Water near electronics requires power-off wiring, containment, and low-voltage caution.

Safety acknowledgements are warnings-only by product decision. The app does not block tutorial progress behind safety confirmations.

## Privacy

- Audience is 13-17.
- Signup collects username, private email, password, and display name.
- Do not collect full name, school, address, precise location, phone number, or social handle.
- Public project pages show display name only.
- Lesson Dev Logs are private.
- Public project writeups are text-only.
- Email verification is required before public publishing.

## Public Text Risk

The product plan does not include pre-publication review, public complaint workflow, public removal workflow, public discussion UI, media uploads, or automated personal-information scanning. This is a deliberate low-friction decision and should be revisited before broad adoption.

## Content Safety

Admin publish checks must confirm hardware warnings, original content, working links, and no copied proprietary explanations. References should link to source material without reproducing protected lesson content.

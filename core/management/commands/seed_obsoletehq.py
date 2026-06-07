from django.core.management.base import BaseCommand
from django.utils.text import slugify

from debugging.models import DebugCard
from gamification.models import Badge
from learning.models import (
    Component,
    ComponentAsset,
    ComponentResource,
    CoreRunWeek,
    Kit,
    LearningExperience,
    LearningExperienceSection,
    SafetyWarning,
    Track,
)


TRACKS = [
    "Getting Started and Setup",
    "First Output",
    "Programming Basics Through Hardware",
    "Analog Input",
    "PWM, RGB, and Sound",
    "Buttons, Switches, and Digital Inputs",
    "Transistors, Relay, Power, and Safety",
    "Displays",
    "Microchips and Output Expansion",
    "Environmental Sensors",
    "Movement and Actuators",
    "Controllers and Human Interfaces",
    "Infrared and RFID",
    "Distance, Obstacle, and Robot-Style Sensing",
    "MPU6050 Motion and IMU",
    "WS2812 / NeoPixel LEDs",
    "Wi-Fi and IoT",
    "Bluetooth",
    "Better Code and Project Structure",
    "Mini Projects and Milestones",
    "Capstone Projects",
]


class Command(BaseCommand):
    help = "Seed ObsoleteHQ structural data without publishing fake lesson content."

    def seed_component(self, *, slug, defaults, kits, assets, resources):
        component, _ = Component.objects.update_or_create(slug=slug, defaults=defaults)
        component.kits.set(kits)

        component.assets.all().delete()
        for order, asset in enumerate(assets, start=1):
            ComponentAsset.objects.create(component=component, order=order, **asset)

        component.resources.all().delete()
        for order, resource in enumerate(resources, start=1):
            ComponentResource.objects.create(component=component, order=order, **resource)
        return component

    def seed_lesson(self, *, code, defaults, required_kits, required_components, safety_warnings, sections):
        lesson, _ = LearningExperience.objects.update_or_create(code=code, defaults=defaults)
        lesson.required_kits.set(required_kits)
        lesson.required_components.set(required_components)
        lesson.safety_warnings.set(safety_warnings)
        if lesson.core_run_week:
            CoreRunWeek.objects.get(week_number=lesson.core_run_week).anchor_learning_experiences.add(lesson)

        lesson.sections.exclude(order__in=[section["order"] for section in sections]).delete()
        for section in sections:
            LearningExperienceSection.objects.update_or_create(
                learning_experience=lesson,
                order=section["order"],
                defaults={
                    "title": section["title"],
                    "section_type": section["section_type"],
                    "body": section["body"],
                    "static_asset_path": section.get("static_asset_path", ""),
                    "static_asset_alt": section.get("static_asset_alt", ""),
                    "static_asset_caption": section.get("static_asset_caption", ""),
                    "static_asset_source_name": section.get("static_asset_source_name", ""),
                    "static_asset_source_url": section.get("static_asset_source_url", ""),
                    "published": True,
                },
            )
        return lesson

    def handle(self, *args, **options):
        pico, _ = Kit.objects.update_or_create(
            slug="sunfounder-pico-2w-ultimate-starter-kit",
            defaults={
                "name": "SunFounder Raspberry Pi Pico 2 W Ultimate Starter Kit",
                "description": "Recommended starter kit for the full ObsoleteHQ learning path.",
                "source_vendor": "SunFounder",
                "url": "https://www.amazon.com/dp/B0DYJ6L46J",
                "recommended": True,
            },
        )
        sensors, _ = Kit.objects.update_or_create(
            slug="37-in-1-sensor-module-starter-kit",
            defaults={
                "name": "37 in 1 Sensor Module Starter Kit",
                "description": "Recommended sensor kit for experiments, remixes, and inventions.",
                "source_vendor": "Generic",
                "url": "https://www.amazon.com/dp/B07LBL7L74",
                "recommended": True,
            },
        )

        tracks = []
        for number, title in enumerate(TRACKS):
            track, _ = Track.objects.update_or_create(
                number=number,
                defaults={
                    "title": title,
                    "slug": slugify(f"track-{number}-{title}"),
                    "description": f"Structural track for {title}.",
                    "order": number,
                    "published": True,
                },
            )
            tracks.append(track)

        for week_number, track in enumerate(tracks, start=1):
            CoreRunWeek.objects.update_or_create(
                week_number=week_number,
                defaults={
                    "title": track.title,
                    "track": track,
                    "theme": track.title,
                    "goal": f"Build confidence with {track.title.lower()}.",
                    "summary": "Anchor lessons appear here after staff publish them.",
                    "estimated_time": "One focused week or club-style session",
                    "published": True,
                },
            )

        components = [
            ("Raspberry Pi Pico 2 W", Component.SignalType.OTHER, "3.3V logic board"),
            ("Breadboard", Component.SignalType.OTHER, "Passive wiring board"),
            ("LED", Component.SignalType.DIGITAL, "Use a resistor"),
            ("Resistor", Component.SignalType.OTHER, "Current limiting"),
            ("Potentiometer", Component.SignalType.ANALOG, "3.3V analog input"),
            ("DHT11 Sensor", Component.SignalType.DIGITAL, "3.3V data signal"),
            ("Servo", Component.SignalType.PWM, "Use appropriate power"),
            ("MFRC522 RFID Module", Component.SignalType.SPI, "Check 3.3V compatibility"),
            ("I2C LCD1602", Component.SignalType.I2C, "Check backpack voltage"),
            ("WS2812 / NeoPixel LEDs", Component.SignalType.DIGITAL, "Use safe current planning"),
        ]
        for name, signal, power in components:
            component, _ = Component.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": f"Core component used in ObsoleteHQ projects: {name}.",
                    "signal_type": signal,
                    "power_requirement": power,
                    "voltage_notes": "Verify 3.3V-safe wiring before connecting to Pico GPIO.",
                    "safety_notes": "Power off while wiring. Double-check polarity and pin labels.",
                    "common_mistakes": "Wrong pin, reversed polarity, missing ground, or 5V signal into GPIO.",
                },
            )
            component.kits.add(pico)
            if "Sensor" in name or "RFID" in name:
                component.kits.add(sensors)

        sf_component_source = "SunFounder Pico 2 W Starter Kit documentation, Components section, © 2026 SunFounder."
        RT = ComponentResource.ResourceType
        BASIC_SOURCE = "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/component/"

        self.seed_component(
            slug="breadboard",
            defaults={
                "name": "Breadboard",
                "category": "Basic",
                "description": (
                    "A solderless breadboard is a reusable prototyping board. The holes are not all separate: hidden metal strips connect groups of holes so parts and wires can share the same electrical node."
                ),
                "how_it_is_used": (
                    "Students use it as the workbench for almost every first circuit. Put the Pico beside or across the breadboard, add parts into the rows, and use jumper wires to connect power, ground, and signals without soldering."
                ),
                "signal_type": Component.SignalType.OTHER,
                "power_requirement": "Passive part. It carries whatever low-voltage rails and signals you wire into it.",
                "pins": "Breadboard holes are grouped internally; the exact row/rail pattern depends on the board.",
                "pinout_notes": (
                    "On a common solderless breadboard, each five-hole row on either side of the center gap is connected internally. The long side rails are usually used for power and ground, but some rails are split in the middle. Always verify rail continuity before trusting a long rail."
                ),
                "voltage_notes": "The breadboard does not make a circuit safer by itself. Pico GPIO still needs 3.3V-safe signals.",
                "safety_notes": "Power off before moving wires. Keep metal legs from touching across rows by accident.",
                "common_mistakes": (
                    "Forgetting the center gap, using a split power rail as if it were continuous, putting both legs of a component in the same connected row, and trusting wire colors instead of tracing the actual path."
                ),
                "source_name": "SunFounder Breadboard component page",
                "source_url": f"{BASIC_SOURCE}component_breadboard.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Breadboard",
                    "static_asset_path": "img/parts/basic/breadboard.png",
                    "alt_text": "Solderless breadboard used for prototyping circuits",
                    "caption": "The reusable board students use to build circuits without soldering.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/breadboard.png",
                },
                {
                    "title": "Internal connections",
                    "static_asset_path": "img/parts/basic/breadboard_internal.png",
                    "alt_text": "Diagram of breadboard internal metal strip connections",
                    "caption": "Hidden strips connect groups of holes under the plastic.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/breadboard_internal.png",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: Breadboard",
                    "url": f"{BASIC_SOURCE}component_breadboard.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page used for the breadboard overview and images.",
                },
            ],
        )

        self.seed_component(
            slug="jumper-wires",
            defaults={
                "name": "Jumper Wires",
                "category": "Basic",
                "description": "Jumper wires are short reusable wires with connector ends for moving signals and power between the Pico, breadboard, and modules.",
                "how_it_is_used": (
                    "Use male-to-male wires for breadboard rows, female-to-female wires for pin headers, and male-to-female wires when one side goes into a breadboard and the other side plugs onto a module pin."
                ),
                "signal_type": Component.SignalType.OTHER,
                "power_requirement": "Passive wire. It carries the voltage or signal you connect to it.",
                "pins": "Male-to-male, female-to-female, and male-to-female ends are all possible.",
                "pinout_notes": "Wire color is only a label. Red is not automatically power and black is not automatically ground unless you wire it that way.",
                "voltage_notes": "A jumper wire can carry a dangerous-to-GPIO voltage if you connect it to one. Trace both ends before powering the circuit.",
                "safety_notes": "Avoid loose wire ends touching neighboring pins. Replace wires with bent, weak, or unreliable connectors.",
                "common_mistakes": "Using color as proof, missing the breadboard row by one hole, plugging into the wrong header pin, and forgetting that a loose ground wire breaks the whole circuit.",
                "source_name": "SunFounder Jumper Wires component page",
                "source_url": f"{BASIC_SOURCE}component_wire.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Jumper wire types",
                    "static_asset_path": "img/parts/basic/wire.png",
                    "alt_text": "Different jumper wire connector types",
                    "caption": "Different end styles let breadboards and modules connect to each other.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/wire.png",
                }
            ],
            resources=[
                {
                    "title": "SunFounder: Jumper Wires",
                    "url": f"{BASIC_SOURCE}component_wire.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page used for wire types and image attribution.",
                }
            ],
        )

        self.seed_component(
            slug="resistor",
            defaults={
                "name": "Resistor",
                "category": "Basic",
                "description": "A resistor limits current and sets voltage/current behavior in a circuit. In student projects it often protects LEDs, creates pull-up or pull-down behavior, or forms a voltage divider.",
                "how_it_is_used": "Use a resistor in series with an LED, as a pull resistor for inputs, or paired with another resistor/sensor to make a voltage divider for analog readings.",
                "signal_type": Component.SignalType.OTHER,
                "power_requirement": "Passive part. Choose a resistance and power rating that fits the circuit.",
                "pins": "Two non-polarized leads. Either end can face either direction.",
                "pinout_notes": "Color bands encode the resistance value. Four- and five-band resistors are common. A 220 ohm resistor is often used for LED current limiting in beginner circuits.",
                "datasheet_notes": "Generic through-hole resistors are selected by resistance, tolerance, and power rating rather than a single module datasheet.",
                "voltage_notes": "A resistor can reduce current, but it is not a magic 5V-to-3.3V adapter for every situation. For Pico inputs, verify the voltage at the GPIO pin.",
                "safety_notes": "If a resistor gets hot, the circuit is drawing too much current or the resistor power rating is too low.",
                "common_mistakes": "Reading the color bands from the wrong end, using 220 ohm where 10k ohm was expected, forgetting the resistor in an LED circuit, and building a voltage divider with swapped values.",
                "source_name": "SunFounder Resistor component page",
                "source_url": f"{BASIC_SOURCE}component_resistor.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Resistor",
                    "static_asset_path": "img/parts/basic/resistor.png",
                    "alt_text": "Through-hole resistors",
                    "caption": "Fixed resistors limit current and set circuit behavior.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/resistor.png",
                },
                {
                    "title": "Resistor symbols",
                    "static_asset_path": "img/parts/basic/resistor_symbol.png",
                    "alt_text": "Circuit symbols for resistors",
                    "caption": "Schematic symbols tell you a resistor belongs in that spot.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/resistor_symbol.png",
                },
                {
                    "title": "Color code card",
                    "static_asset_path": "img/parts/basic/resistance_card.jpg",
                    "alt_text": "Resistor color code reference card",
                    "caption": "Use color bands to identify resistance before wiring.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/resistance_card.jpg",
                },
                {
                    "title": "220 ohm example",
                    "static_asset_path": "img/parts/basic/220ohm.jpg",
                    "alt_text": "220 ohm resistor color bands",
                    "caption": "A common LED current-limiting resistor value.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/220ohm.jpg",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: Resistor",
                    "url": f"{BASIC_SOURCE}component_resistor.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for resistor explanation, color code images, and 220 ohm example.",
                },
                {
                    "title": "Wikipedia: Resistor",
                    "url": "https://en.wikipedia.org/wiki/Resistor",
                    "resource_type": RT.GUIDE,
                    "notes": "General background reference for resistor behavior and terminology.",
                },
            ],
        )

        self.seed_component(
            slug="transistor",
            defaults={
                "name": "Transistor",
                "category": "Basic",
                "description": "A transistor is a semiconductor part that lets a small control signal influence a larger current path. In beginner Pico projects it is usually used as an electronic switch.",
                "how_it_is_used": "Use a transistor when the Pico should control a load that needs more current than a GPIO pin can safely provide, such as a small motor, relay coil, or buzzer circuit.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "The Pico drives the base through a resistor; the load uses its own suitable supply path.",
                "pins": "B, C, E: base, collector, emitter. Pin order depends on the exact part package.",
                "pinout_notes": "SunFounder notes that S8050 is NPN and S8550 is PNP. Check the printed label carefully because the packages look similar.",
                "datasheet_notes": "Check the exact part marking before using a datasheet. Important values include maximum collector current, voltage ratings, gain, and package pin order.",
                "main_component": "S8050 NPN transistor and S8550 PNP transistor are identified in the SunFounder component page.",
                "discrete_parts": "A transistor switch normally needs a base resistor. Inductive loads such as motors and relays also need flyback protection handled by the circuit design.",
                "voltage_notes": "The Pico GPIO controls only the base signal. Do not drive a load directly from GPIO; keep load current out of the Pico pin.",
                "safety_notes": "Use the right transistor type and orientation. A reversed transistor or missing base resistor can make the circuit fail or overheat.",
                "common_mistakes": "Swapping collector and emitter, confusing S8050 and S8550, forgetting the shared ground, skipping the base resistor, and expecting a GPIO pin to power the load.",
                "source_name": "SunFounder Transistor component page",
                "source_url": f"{BASIC_SOURCE}component_transistor.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "NPN and PNP transistors",
                    "static_asset_path": "img/parts/basic/npn-pnp.png",
                    "alt_text": "NPN and PNP transistor illustrations",
                    "caption": "The kit uses both NPN and PNP transistor types.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/NPN%26PNP.png",
                },
                {
                    "title": "Transistor symbols",
                    "static_asset_path": "img/parts/basic/transistor_symbol.png",
                    "alt_text": "NPN and PNP transistor schematic symbols",
                    "caption": "The emitter arrow helps distinguish NPN and PNP symbols.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/transistor_symbol.png",
                },
                {
                    "title": "Emitter, base, collector",
                    "static_asset_path": "img/parts/basic/ebc.png",
                    "alt_text": "Transistor emitter base collector pin reference",
                    "caption": "Always verify the pin order for the exact transistor in hand.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/ebc.png",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: Transistor",
                    "url": f"{BASIC_SOURCE}component_transistor.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for S8050/S8550 identification and transistor diagrams.",
                },
                {
                    "title": "AllDataSheet: UTC S8050",
                    "url": "https://www.alldatasheet.com/html-pdf/172696/UTC/S8050/52/1/S8050.html",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated reference page for an S8050 NPN transistor datasheet. Match markings before applying it.",
                },
                {
                    "title": "Mouser: SS8550 datasheet",
                    "url": "https://www.mouser.com/datasheet/2/149/SS8550-118608.pdf",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated distributor datasheet link for an SS8550 PNP transistor.",
                },
                {
                    "title": "Wikipedia: P-N junction",
                    "url": "https://en.wikipedia.org/wiki/P-n_junction",
                    "resource_type": RT.GUIDE,
                    "notes": "Background reference for the semiconductor junction concept SunFounder mentions.",
                },
            ],
        )

        self.seed_component(
            slug="capacitor",
            defaults={
                "name": "Capacitor",
                "category": "Basic",
                "description": "A capacitor stores electric charge. In circuits it is used for smoothing, filtering, timing, coupling, and short-term energy storage.",
                "how_it_is_used": "Students will see capacitors across power rails to smooth noise, near modules to steady power, and in timing or sensor circuits.",
                "signal_type": Component.SignalType.OTHER,
                "power_requirement": "Passive part. Choose capacitance, voltage rating, and polarity/type for the circuit.",
                "pins": "Ceramic capacitors are usually non-polarized. Electrolytic capacitors are polarized and must face the correct direction.",
                "pinout_notes": "SunFounder notes the kit uses ceramic and electrolytic capacitors. Ceramic labels such as 103 and 104 encode picofarad values: 103 means 10 x 10^3 pF and 104 means 10 x 10^4 pF.",
                "datasheet_notes": "Generic capacitors are selected by capacitance, voltage rating, tolerance, dielectric/type, polarity, and package.",
                "voltage_notes": "Use a voltage rating higher than the voltage in the circuit. Never reverse a polarized electrolytic capacitor.",
                "safety_notes": "Small kit capacitors are low-energy parts, but reversed electrolytic capacitors can heat, leak, or fail.",
                "common_mistakes": "Reading 104 as 104 pF instead of 100 nF, reversing electrolytic polarity, using too low a voltage rating, and expecting a capacitor to fix a wiring mistake.",
                "source_name": "SunFounder Capacitor component page",
                "source_url": f"{BASIC_SOURCE}component_capacitor.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Capacitors",
                    "static_asset_path": "img/parts/basic/capacitor.png",
                    "alt_text": "Capacitors from the electronics kit",
                    "caption": "The kit uses ceramic and electrolytic capacitor types.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/capacitor.png",
                }
            ],
            resources=[
                {
                    "title": "SunFounder: Capacitor",
                    "url": f"{BASIC_SOURCE}component_capacitor.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for capacitor type and label notes.",
                },
                {
                    "title": "Wikipedia: Ceramic capacitor",
                    "url": "https://en.wikipedia.org/wiki/Ceramic_capacitor",
                    "resource_type": RT.GUIDE,
                    "notes": "General reference for ceramic capacitor behavior and construction.",
                },
                {
                    "title": "Wikipedia: Electrolytic capacitor",
                    "url": "https://en.wikipedia.org/wiki/Electrolytic_capacitor",
                    "resource_type": RT.GUIDE,
                    "notes": "General reference for polarized electrolytic capacitors.",
                },
            ],
        )

        self.seed_component(
            slug="diode",
            defaults={
                "name": "Diode",
                "category": "Basic",
                "description": "A diode is a two-terminal semiconductor part that conducts much more easily in one direction than the other.",
                "how_it_is_used": "Students use diodes for polarity protection, signal steering, rectifying, and flyback protection around coils or motors when the circuit calls for it.",
                "signal_type": Component.SignalType.OTHER,
                "power_requirement": "Passive semiconductor. Select current, voltage, and diode type for the job.",
                "pins": "Anode and cathode. The cathode is commonly marked by a band.",
                "pinout_notes": "Conventional current flows from anode to cathode when the diode is forward biased. Reverse bias blocks current except for leakage and breakdown behavior.",
                "datasheet_notes": "Important values include forward voltage, maximum average current, reverse voltage, switching speed, and package/polarity marking.",
                "voltage_notes": "Diodes have a forward voltage drop. They are directional, so flipping one changes the circuit behavior.",
                "safety_notes": "Use the correct orientation and current rating. A diode installed backward can stop a circuit from working or leave a load unprotected.",
                "common_mistakes": "Ignoring the cathode band, assuming every diode is an LED, choosing a slow/weak diode for a switching job, and forgetting flyback protection for coils.",
                "source_name": "SunFounder Diode component page",
                "source_url": f"{BASIC_SOURCE}component_diode.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Diode symbol and direction",
                    "static_asset_path": "img/parts/basic/diode_symbol.png",
                    "alt_text": "Diode symbol and direction diagram",
                    "caption": "Diodes are directional components with an anode and cathode.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/Diodes-symbol.png",
                }
            ],
            resources=[
                {
                    "title": "SunFounder: Diode",
                    "url": f"{BASIC_SOURCE}component_diode.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for diode behavior and polarity discussion.",
                },
                {
                    "title": "Wikipedia: Diode",
                    "url": "https://en.wikipedia.org/wiki/Diode",
                    "resource_type": RT.GUIDE,
                    "notes": "General reference for diode types and behavior.",
                },
                {
                    "title": "Diodes Inc: 1N5819HW datasheet",
                    "url": "https://www.diodes.com/assets/Datasheets/ds30217.pdf",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated Schottky diode datasheet link useful when comparing diode ratings; match the exact part marking before use.",
                },
            ],
        )

        self.seed_component(
            slug="li-po-charger-module",
            defaults={
                "name": "Li-po Charger Module",
                "category": "Basic",
                "description": "A small module that lets a Pico project charge and run from a single-cell Li-po battery when used as SunFounder shows.",
                "how_it_is_used": "The module plugs into the breadboard with the Pico, connects to a Li-po battery through a PH2.0 connector, charges from USB power, and can switch the Pico project to battery power when USB is removed.",
                "signal_type": Component.SignalType.POWER,
                "power_requirement": "Input 5V, output 3.3V per SunFounder. Battery connector is PH2.0.",
                "pins": "P1: VBUS, VSYS, GND. P2: BAT and GND battery connector.",
                "pinout_notes": "The SunFounder schematic labels P1 pins as VBUS, VSYS, and GND, and P2 as the battery connector. Do not treat the battery connector as a GPIO header.",
                "datasheet_notes": "The SunFounder schematic identifies U1 as LTC4054 and D2 as B5819W. Use exact board markings and schematic labels before applying any datasheet.",
                "main_component": "LTC4054 charger IC, identified in the SunFounder schematic image.",
                "discrete_parts": "SunFounder schematic labels include D1 charge indicator LED, R1 2k, R2 3k, C1 10uF, C2 0.1uF, and D2 B5819W Schottky diode.",
                "libraries": "No MicroPython library is needed. This is a power module, not a sensor.",
                "voltage_notes": "SunFounder lists 5V input and 3.3V output. The battery side is for a single-cell Li-po battery; do not connect random batteries or higher-voltage packs.",
                "safety_notes": "Battery charging deserves extra care. Use the intended connector and battery type, stop if anything heats up, and avoid shorts around the battery leads.",
                "common_mistakes": "Leaving the charger attached while trying to connect the Pico to a weak USB port, mixing up VBUS and VSYS, shorting the battery connector, or assuming this module can charge any battery chemistry.",
                "source_name": "SunFounder Li-po Charger Module component page",
                "source_url": f"{BASIC_SOURCE}component_lipo_charger.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "Li-po charger module",
                    "static_asset_path": "img/parts/basic/lipo_module.png",
                    "alt_text": "Li-po charger module for Raspberry Pi Pico boards",
                    "caption": "The compact board used for Pico battery charging and power handoff.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/lipo_module.png",
                },
                {
                    "title": "Breadboard wiring",
                    "static_asset_path": "img/parts/basic/lipo_wire.png",
                    "alt_text": "Li-po charger module wired with a Raspberry Pi Pico on a breadboard",
                    "caption": "SunFounder shows the module plugged into the breadboard with the Pico.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/lipo_wire.png",
                },
                {
                    "title": "Schematic",
                    "static_asset_path": "img/parts/basic/sch_lipo_charger.png",
                    "alt_text": "Schematic for the Li-po charger module",
                    "caption": "The schematic identifies the charger IC, diode, connector pins, resistors, capacitors, and indicator LED.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/sch_lipo_charger.png",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: Li-po Charger Module",
                    "url": f"{BASIC_SOURCE}component_lipo_charger.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for module use, feature list, warning note, and images.",
                },
                {
                    "title": "Diodes Inc: B5819W datasheet",
                    "url": "https://www.diodes.com/assets/Datasheets/ds30217.pdf",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated datasheet link for the B5819W Schottky diode called out in the SunFounder schematic.",
                },
            ],
        )

        self.seed_component(
            slug="74hc595",
            defaults={
                "name": "74HC595",
                "category": "Chip",
                "description": (
                    "The 74HC595 is an 8-bit serial-in, parallel-out shift register with a storage register and tri-state outputs. It lets a Pico control more output pins while using only a few GPIO signals."
                ),
                "how_it_is_used": (
                    "Students use it when one Pico pin at a time is not enough, such as driving rows of LEDs, a 7-segment display, a 4-digit display, or an LED matrix through a few control lines."
                ),
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "Use a logic supply compatible with the circuit. With Pico projects, keep the logic side 3.3V-safe unless a level-shifting design is intentionally used.",
                "pins": "DS serial data, SHcp shift-register clock, STcp storage/latch clock, MR active-low reset, OE active-low output enable, Q0-Q7 parallel outputs, Q7' serial output, VCC, GND.",
                "pinout_notes": (
                    "SunFounder notes that data shifts on the rising edge of SHcp and transfers to the storage register on the rising edge of STcp. OE must be low for outputs to drive the bus, and MR must be high to avoid resetting the register."
                ),
                "datasheet_notes": (
                    "The TI CD74HC595 datasheet covers supply range, input thresholds, output current limits, timing, and the exact pinout. Check current limits before trying to drive many LEDs directly."
                ),
                "main_component": "74HC595 8-bit shift register / storage register IC.",
                "discrete_parts": "A useful 74HC595 output circuit usually adds current-limiting resistors for LEDs and may need transistor drivers when the load current is too high for the chip.",
                "libraries": (
                    "No special MicroPython library is required. Students usually use machine.Pin plus bit-banging for DS/SHcp/STcp, or SPI-style output for more advanced projects."
                ),
                "voltage_notes": "Do not power the chip at 5V and connect its outputs or inputs directly to Pico GPIO unless the circuit has been checked for 3.3V compatibility.",
                "safety_notes": "The chip expands outputs; it does not increase safe current. Respect per-pin and total current limits.",
                "common_mistakes": (
                    "Leaving OE floating, pulling MR low by accident, swapping SHcp and STcp, forgetting current-limiting resistors for LEDs, and expecting Q0-Q7 to update before the latch clock."
                ),
                "source_name": "SunFounder 74HC595 component page",
                "source_url": f"{BASIC_SOURCE}component_74hc595.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "74HC595 IC",
                    "static_asset_path": "img/parts/chip/74hc595.png",
                    "alt_text": "74HC595 integrated circuit",
                    "caption": "The shift-register chip used to turn serial data into eight parallel outputs.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/74HC595.png",
                },
                {
                    "title": "74HC595 pinout",
                    "static_asset_path": "img/parts/chip/74hc595_pin.png",
                    "alt_text": "74HC595 pin function diagram",
                    "caption": "Pin functions for serial input, clocks, reset, output enable, outputs, power, and ground.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/74hc595_pin.png",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: 74HC595",
                    "url": f"{BASIC_SOURCE}component_74hc595.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for 74HC595 behavior, pin functions, examples, and images.",
                },
                {
                    "title": "Texas Instruments: CD74HC595 datasheet",
                    "url": "https://www.ti.com/lit/ds/symlink/cd74hc595.pdf?ts=1617341564801",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated datasheet link used for electrical limits, timing, and pin details.",
                },
            ],
        )

        self.seed_component(
            slug="ta6586-motor-driver-chip",
            defaults={
                "name": "TA6586 - Motor Driver Chip",
                "category": "Chip",
                "description": (
                    "The TA6586 is a monolithic motor-driver IC for bidirectional DC motors. It accepts two logic input signals to control forward, reverse, brake, and stop behavior."
                ),
                "how_it_is_used": (
                    "Students use it between the Pico and a motor or pump. The Pico sends logic signals, while the TA6586 handles the higher-current motor path and direction control."
                ),
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "Motor supply depends on the motor circuit. Logic inputs come from Pico GPIO; motor current must not pass through the Pico GPIO pins.",
                "pins": "SunFounder provides a pin-function diagram for the DIP8 TA6586 package. Use that diagram and the datasheet before wiring.",
                "pinout_notes": (
                    "The important student rule is separation of jobs: Pico GPIO controls the input pins, motor power goes through the driver, and all related grounds must be connected correctly."
                ),
                "datasheet_notes": (
                    "SunFounder lists low standby current, wide supply voltage range, brake function, thermal shutdown, over-current limiting, short-circuit protection, and DIP8 Pb-free package. Check the datasheet for exact voltage/current limits before selecting a motor."
                ),
                "main_component": "TA6586 bidirectional DC motor driver IC.",
                "discrete_parts": (
                    "SunFounder notes the chip includes built-in clamp diode behavior for inductive load current. Real motor circuits still need appropriate supply decoupling, wiring, and current planning."
                ),
                "libraries": "No dedicated MicroPython library is needed. Students usually drive the two control inputs with machine.Pin or PWM-capable pins if the lesson uses speed control.",
                "voltage_notes": "Do not connect a motor directly to Pico GPIO. Keep GPIO input signals within Pico-safe logic levels and size the motor supply for the motor.",
                "safety_notes": "Motors and pumps can draw more current at startup or when stalled. Stop testing if the chip, battery, or wires heat up.",
                "common_mistakes": "Using GPIO as motor power, forgetting common ground, wiring the two inputs backward, ignoring the truth table, and choosing a motor that exceeds the driver limits.",
                "source_name": "SunFounder TA6586 component page",
                "source_url": f"{BASIC_SOURCE}component_ta6585.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "TA6586 IC",
                    "static_asset_path": "img/parts/chip/ta6586.png",
                    "alt_text": "TA6586 motor driver chip",
                    "caption": "The motor-driver chip used for bidirectional DC motor control.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/ta6586.png",
                },
                {
                    "title": "TA6586 pin function",
                    "static_asset_path": "img/parts/chip/ta6586_pin.png",
                    "alt_text": "TA6586 pin function diagram",
                    "caption": "SunFounder pin function reference for the TA6586 package.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/ta6586_pin.png",
                },
                {
                    "title": "TA6586 input truth table",
                    "static_asset_path": "img/parts/chip/ta6586_principle.png",
                    "alt_text": "TA6586 input truth table",
                    "caption": "Input combinations determine stop, forward, reverse, and brake behavior.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/ta6586_priciple.png",
                },
            ],
            resources=[
                {
                    "title": "SunFounder: TA6586 - Motor Driver Chip",
                    "url": f"{BASIC_SOURCE}component_ta6585.html",
                    "resource_type": RT.SUNFOUNDER,
                    "notes": "Source page for TA6586 features, pin function diagram, input truth table, and examples.",
                },
                {
                    "title": "Components101: TA6586 datasheet PDF",
                    "url": "https://components101.com/sites/default/files/component_datasheet/ta6586-datasheet.pdf",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated datasheet PDF link for TA6586 electrical and package reference.",
                },
                {
                    "title": "AllDataSheet: RZ-MIC TA6586",
                    "url": "https://www.alldatasheet.com/datasheet-pdf/pdf/1761575/RZ-MIC/TA6586.html",
                    "resource_type": RT.DATASHEET,
                    "notes": "Validated datasheet reference page for cross-checking TA6586 details.",
                },
            ],
        )

        self.seed_component(
            slug="led",
            defaults={
                "name": "LED",
                "category": "Display",
                "description": "An LED is a light-emitting diode: a directional semiconductor part that turns electrical energy into visible light.",
                "how_it_is_used": "Students use single LEDs for first outputs, status indicators, traffic lights, alarms, and debugging signals. A Pico pin can switch an LED on/off or use PWM to dim it.",
                "signal_type": Component.SignalType.PWM,
                "power_requirement": "Use a current-limiting resistor in series. SunFounder notes typical red/yellow/green forward voltage around 1.8V, white around 2.6V, and common LED current up to 20mA.",
                "pins": "Anode and cathode. SunFounder notes the longer leg is the anode and the shorter leg is the cathode.",
                "pinout_notes": "The LED conducts one way. Anode goes toward the positive side of the circuit, cathode toward the lower-voltage side or ground path.",
                "datasheet_notes": "SunFounder does not identify one exact LED part number. For a real LED datasheet, match the color, package size, and manufacturer; key values are forward voltage, recommended current, viewing angle, and brightness.",
                "discrete_parts": "A current-limiting resistor is required in typical Pico LED circuits.",
                "libraries": "Use machine.Pin for on/off control and machine.PWM for dimming or fading.",
                "voltage_notes": "Do not connect an LED directly across a supply or GPIO without current limiting.",
                "safety_notes": "Bright LEDs can be uncomfortable at close range. Keep current low and avoid staring into high-brightness LEDs.",
                "common_mistakes": "Reversing polarity, forgetting the resistor, using too small a resistor, assuming every LED color has the same forward voltage, and trying to power too many LEDs from one GPIO pin.",
                "source_name": "SunFounder LED component page",
                "source_url": f"{BASIC_SOURCE}component_led.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {
                    "title": "LED",
                    "static_asset_path": "img/parts/display/led.png",
                    "alt_text": "Light emitting diodes in several colors",
                    "caption": "A simple output part used in the first Pico circuits.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/LED.png",
                },
                {
                    "title": "LED symbol",
                    "static_asset_path": "img/parts/display/led_symbol.png",
                    "alt_text": "LED schematic symbol",
                    "caption": "The diode symbol reminds you that LED direction matters.",
                    "source_name": sf_component_source,
                    "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/led_symbol.png",
                },
            ],
            resources=[
                {"title": "SunFounder: LED", "url": f"{BASIC_SOURCE}component_led.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for LED polarity, forward voltage notes, current limit formula, and images."},
                {"title": "Wikipedia: Light-emitting diode", "url": "https://en.wikipedia.org/wiki/Light-emitting_diode", "resource_type": RT.GUIDE, "notes": "General reference for LED operation and terminology."},
                {"title": "MicroPython: machine.Pin", "url": "https://docs.micropython.org/en/latest/library/machine.Pin.html", "resource_type": RT.LIBRARY, "notes": "Use for basic digital LED on/off control."},
                {"title": "MicroPython: machine.PWM", "url": "https://docs.micropython.org/en/latest/library/machine.PWM.html", "resource_type": RT.LIBRARY, "notes": "Use for LED fading and brightness control."},
            ],
        )

        self.seed_component(
            slug="rgb-led",
            defaults={
                "name": "RGB LED",
                "category": "Display",
                "description": "An RGB LED packages red, green, and blue LEDs together so a circuit can mix colors by controlling each channel.",
                "how_it_is_used": "Students use it for color indicators, mood lights, feedback states, and PWM color-mixing projects.",
                "signal_type": Component.SignalType.PWM,
                "power_requirement": "Common cathode RGB LED. Each color channel needs its own current-limiting resistor.",
                "pins": "Four pins: common cathode plus red, green, and blue. SunFounder notes the longest pin is the common cathode; the adjacent left pin is red, and the two right pins are green and blue.",
                "pinout_notes": "The kit uses a common cathode RGB LED, so the shared pin goes to GND and each color pin is driven high through current limiting.",
                "datasheet_notes": "SunFounder lists: common cathode, 5mm clear round lens, red forward voltage DC 2.0-2.2V, blue/green DC 3.0-3.2V at 20mA, 0.06W DIP RGB LED, and 30 degree viewing angle.",
                "libraries": "Use three PWM outputs with machine.PWM for color mixing.",
                "voltage_notes": "Each color has a different forward voltage, so resistor values and brightness can differ by channel.",
                "safety_notes": "Do not drive any color channel without current limiting. Keep total current within Pico and power-source limits.",
                "common_mistakes": "Treating it like one LED, using only one resistor on the common pin, mixing up common anode and common cathode code, and swapping red/green/blue pins.",
                "source_name": "SunFounder RGB LED component page",
                "source_url": f"{BASIC_SOURCE}component_rgb_led.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "RGB LED", "static_asset_path": "img/parts/display/rgb_led.png", "alt_text": "RGB LED component", "caption": "Three LEDs in one package for color mixing.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/rgb_led.png"},
                {"title": "Color mixing", "static_asset_path": "img/parts/display/rgb_light.png", "alt_text": "RGB light color mixing diagram", "caption": "Red, green, and blue channels combine into many colors.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/rgb_light.png"},
                {"title": "RGB LED symbol", "static_asset_path": "img/parts/display/rgb_symbol.png", "alt_text": "RGB LED schematic symbol", "caption": "The symbol shows three LED channels in one part.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/rgb_symbol.png"},
                {"title": "RGB LED pinout", "static_asset_path": "img/parts/display/rgb_pin.jpg", "alt_text": "RGB LED pinout reference", "caption": "SunFounder pin reference for the common cathode RGB LED.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/rgb_pin.jpg"},
            ],
            resources=[
                {"title": "SunFounder: RGB LED", "url": f"{BASIC_SOURCE}component_rgb_led.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for common-cathode type, pinout, feature list, and images."},
                {"title": "MicroPython: machine.PWM", "url": "https://docs.micropython.org/en/latest/library/machine.PWM.html", "resource_type": RT.LIBRARY, "notes": "Use three PWM channels for color mixing."},
            ],
        )

        self.seed_component(
            slug="led-bar-graph",
            defaults={
                "name": "LED Bar Graph",
                "category": "Display",
                "description": "An LED bar graph is a row of individual LEDs in one package, useful for showing levels such as progress, volume, signal strength, or sensor value.",
                "how_it_is_used": "Students drive it like ten separate LEDs, often with one resistor per segment and either direct GPIO or an output-expander/shift-register circuit.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "Each LED segment needs current limiting. Current planning matters if many segments are on at once.",
                "pins": "The bar graph exposes one anode/cathode pair per LED segment. SunFounder notes the labeled side typically represents the anode and the opposite side the cathode.",
                "pinout_notes": "Check the SunFounder pin and schematic images before wiring; treat each bar as a separate LED.",
                "datasheet_notes": "SunFounder does not identify a specific bar graph manufacturer part number. Match the package markings before using a datasheet.",
                "discrete_parts": "Ten LED dies in one package; each segment behaves like a separate LED.",
                "libraries": "No special library is needed; use machine.Pin or drive through a 74HC595 when lessons need fewer Pico GPIO pins.",
                "voltage_notes": "The display package does not include current limiting. Use resistors and stay within current limits.",
                "safety_notes": "Turning all segments on can draw much more current than one LED.",
                "common_mistakes": "Skipping resistors, wiring the labeled side backward, assuming one common pin controls the whole display, and exceeding current limits when all bars are lit.",
                "source_name": "SunFounder LED Bar Graph component page",
                "source_url": f"{BASIC_SOURCE}component_led_bar.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "LED bar graph", "static_asset_path": "img/parts/display/bar_graph.png", "alt_text": "LED bar graph component", "caption": "A row of LEDs in one display package.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/bar_graph.png"},
                {"title": "LED bar pin reference", "static_asset_path": "img/parts/display/led_bar_pin.png", "alt_text": "LED bar graph pin reference", "caption": "Pin side reference from SunFounder.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/led_bar_pin.png"},
                {"title": "LED bar schematic", "static_asset_path": "img/parts/display/led_bar_sche1.png", "alt_text": "LED bar graph internal schematic", "caption": "Internal LED segment schematic.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/led_bar_sche1.png"},
            ],
            resources=[
                {"title": "SunFounder: LED Bar Graph", "url": f"{BASIC_SOURCE}component_led_bar.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for bar graph usage, pin notes, schematic image, and examples."},
                {"title": "MicroPython: machine.Pin", "url": "https://docs.micropython.org/en/latest/library/machine.Pin.html", "resource_type": RT.LIBRARY, "notes": "Use for direct segment on/off control."},
            ],
        )

        self.seed_component(
            slug="7-segment-display",
            defaults={
                "name": "7-segment Display",
                "category": "Display",
                "description": "A 7-segment display uses seven LED segments, plus often a decimal point, to form digits and a few letters.",
                "how_it_is_used": "Students use it for counters, timers, scores, and numeric sensor output, usually with segment codes and sometimes a 74HC595 to save GPIO pins.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "Common cathode display in this kit. Each segment is an LED and needs current limiting.",
                "pins": "Segments a through g plus decimal point, with common cathode pin(s).",
                "pinout_notes": "SunFounder states this kit uses a common cathode display. Segment codes use bits for DP/G/F/E/D/C/B/A; for example 0x3f displays 0.",
                "datasheet_notes": "SunFounder does not identify an exact 7-segment part number. Match the display markings and common-cathode/common-anode type before applying a datasheet.",
                "discrete_parts": "Seven LED segments plus decimal point in one display body.",
                "libraries": "No special library is required; students usually map digits to segment bit patterns and write them with GPIO or a 74HC595.",
                "voltage_notes": "Every lit segment draws current. Use resistors and check total current.",
                "safety_notes": "Do not connect segments directly to GPIO without current limiting.",
                "common_mistakes": "Using common-anode code on a common-cathode display, reversing the common pin, mixing up segment order, and forgetting the decimal point bit.",
                "source_name": "SunFounder 7-segment Display component page",
                "source_url": f"{BASIC_SOURCE}component_7segment.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "7-segment display", "static_asset_path": "img/parts/display/7_segment.png", "alt_text": "Single 7-segment display", "caption": "Seven LED segments form digits.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/7_segment.png"},
                {"title": "Common cathode symbol", "static_asset_path": "img/parts/display/segment_cathode.png", "alt_text": "Common cathode 7-segment display symbol", "caption": "SunFounder symbol for the common cathode display used in the kit.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/segment_cathode.png"},
            ],
            resources=[
                {"title": "SunFounder: 7-segment Display", "url": f"{BASIC_SOURCE}component_7segment.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for common-cathode type, segment code table, and images."},
                {"title": "Wikipedia: Seven-segment display", "url": "https://en.wikipedia.org/wiki/Seven-segment_display", "resource_type": RT.GUIDE, "notes": "General reference for segment displays and encoding concepts."},
            ],
        )

        self.seed_component(
            slug="4-digit-7-segment-display",
            defaults={
                "name": "4-Digit 7-Segment Display",
                "category": "Display",
                "description": "A 4-digit 7-segment display combines four numeric displays and relies on fast multiplexing so the eye sees all digits at once.",
                "how_it_is_used": "Students use it for clocks, timers, counters, and numeric readouts. Code cycles through digits quickly, enabling one digit at a time.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "Each segment path needs current limiting. Multiplexed displays can still draw meaningful total current.",
                "pins": "Shared segment lines plus digit-select lines; use the SunFounder schematic before wiring.",
                "pinout_notes": "SunFounder explains visual persistence: each digit is lit briefly in sequence, typically cycling quickly enough that all four digits appear continuously lit.",
                "datasheet_notes": "SunFounder provides schematic/reference diagrams but not a manufacturer part number. Verify the common type and pinout against markings before using a datasheet.",
                "discrete_parts": "Four 7-segment LED digits in one package.",
                "libraries": "No dedicated library is required; lessons usually combine digit scanning with GPIO or 74HC595 output.",
                "voltage_notes": "Brightness depends on scan timing, resistors, and current limits. Do not compensate for dimness by exceeding safe current.",
                "safety_notes": "Multiplexing errors can leave too many segments on continuously and increase current draw.",
                "common_mistakes": "Scanning too slowly, enabling two digits at once, using the wrong common type, mixing segment order, and forgetting to blank a digit while changing segment data.",
                "source_name": "SunFounder 4-Digit 7-Segment Display component page",
                "source_url": f"{BASIC_SOURCE}component_4_digit_display.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "4-digit display schematic", "static_asset_path": "img/parts/display/4-digit-sche.png", "alt_text": "4-digit 7-segment display schematic", "caption": "Four 7-segment digits work together through fast scanning.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/4-digit-sche.png"},
                {"title": "4-digit common-anode/cathode reference", "static_asset_path": "img/parts/display/4-digit-sche-ca.png", "alt_text": "4-digit 7-segment display reference diagram", "caption": "Reference diagram from the SunFounder component page.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/4-digit-sche-ca.png"},
            ],
            resources=[
                {"title": "SunFounder: 4-Digit 7-Segment Display", "url": f"{BASIC_SOURCE}component_4_digit_display.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for multiplexing explanation, glyph codes, and reference images."},
                {"title": "Wikipedia: Seven-segment display", "url": "https://en.wikipedia.org/wiki/Seven-segment_display", "resource_type": RT.GUIDE, "notes": "General reference for segment naming and display behavior."},
            ],
        )

        self.seed_component(
            slug="led-dot-matrix",
            defaults={
                "name": "LED Dot Matrix",
                "category": "Display",
                "description": "An LED dot matrix is a grid of LEDs arranged in rows and columns for simple icons, patterns, letters, and animations.",
                "how_it_is_used": "Students scan rows and columns rapidly, often using two 74HC595 chips to control the matrix with fewer Pico pins.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "The kit uses a CA dot matrix labeled 788BS. Current limiting and scan timing are required.",
                "pins": "Pins 1-16 map to ROW and COL lines. SunFounder lists COL pins 13, 3, 4, 10, 6, 11, 15, 16 and ROW pins 9, 14, 8, 12, 1, 7, 2, 5.",
                "pinout_notes": "SunFounder states this kit uses a common-anode 788BS matrix. For the top-left LED, set ROW 1 high and COL 1 low; for common cathode the logic is opposite.",
                "datasheet_notes": "The visible part marking is 788BS per SunFounder. Verify the matrix label and common-anode/common-cathode type before using any generic dot-matrix datasheet.",
                "main_component": "788BS common-anode LED dot matrix, identified by SunFounder.",
                "discrete_parts": "An 8x8 grid of LED junctions sharing row and column lines. SunFounder examples use two 74HC595 chips: one for rows and one for columns.",
                "libraries": "No special library is required for the raw matrix; students usually write row/column scan code using GPIO or 74HC595 helper functions.",
                "voltage_notes": "The matrix can light many LEDs, so current-limiting and duty cycle matter.",
                "safety_notes": "Avoid static all-on patterns without current planning.",
                "common_mistakes": "Using common-cathode logic on the common-anode 788BS, rotating the pin numbering, scanning too slowly, and forgetting current limits when many pixels appear lit.",
                "source_name": "SunFounder LED Dot Matrix component page",
                "source_url": f"{BASIC_SOURCE}component_788bs.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "LED dot matrix", "static_asset_path": "img/parts/display/led_matrix.png", "alt_text": "LED dot matrix display", "caption": "A grid display for simple pixel graphics.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/led_matrix.png"},
                {"title": "788BS external view", "static_asset_path": "img/parts/display/led_matrix_external.png", "alt_text": "788BS LED dot matrix external pin reference", "caption": "External view and pin numbering reference.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/image84.png"},
                {"title": "788BS internal structure", "static_asset_path": "img/parts/display/led_matrix_internal.png", "alt_text": "788BS LED dot matrix internal row and column structure", "caption": "Rows and columns share LED connections inside the package.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/image85.png"},
            ],
            resources=[
                {"title": "SunFounder: LED Dot Matrix", "url": f"{BASIC_SOURCE}component_788bs.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for 788BS type, row/column pin table, internal/external images, and examples."},
                {"title": "MicroPython: machine.Pin", "url": "https://docs.micropython.org/en/latest/library/machine.Pin.html", "resource_type": RT.LIBRARY, "notes": "Use for row/column scanning or controlling shift-register lines."},
            ],
        )

        self.seed_component(
            slug="i2c-lcd1602",
            defaults={
                "name": "I2C LCD1602",
                "category": "Display",
                "description": "An LCD1602 is a 16-column by 2-row character display. The I2C backpack reduces the many LCD parallel pins to four useful module pins.",
                "how_it_is_used": "Students use it to show text, sensor readings, menus, and status messages while keeping Pico GPIO usage low.",
                "signal_type": Component.SignalType.I2C,
                "power_requirement": "SunFounder labels VCC as 5V. Confirm the I2C pull-up behavior before connecting to Pico GPIO.",
                "pins": "GND, VCC, SDA, SCL.",
                "pinout_notes": "SunFounder notes SDA and SCL are pulled up to VCC. Default I2C address is usually 0x27, sometimes 0x3F. A0/A1/A2 pads can change the address.",
                "datasheet_notes": "SunFounder identifies the I2C backpack chip as PCF8574. The TI PCF8574 datasheet covers the I/O expander behind the LCD module.",
                "main_component": "PCF8574 I2C I/O expander on the LCD backpack, identified by SunFounder.",
                "discrete_parts": "LCD1602 character LCD, PCF8574 backpack, backlight jumper cap, contrast potentiometer, and address pads A0/A1/A2.",
                "libraries": "Use machine.I2C plus an LCD1602/PCF8574 driver class. The driver should match the module address, usually 0x27 or 0x3F.",
                "voltage_notes": "Because the module is labeled 5V and I2C pull-ups connect to VCC, verify Pico-safe pull-up voltage before direct wiring.",
                "safety_notes": "Power off before changing address pads or wiring. Avoid shorting the backpack pins.",
                "common_mistakes": "Wrong I2C address, no common ground, swapped SDA/SCL, contrast turned until text disappears, backlight jumper removed, and unsafe 5V pull-ups on Pico I2C lines.",
                "source_name": "SunFounder I2C LCD1602 component page",
                "source_url": f"{BASIC_SOURCE}component_i2clcd1602.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "I2C LCD1602", "static_asset_path": "img/parts/display/i2c_lcd1602.png", "alt_text": "I2C LCD1602 character display module", "caption": "A text display with an I2C backpack.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/i2c_lcd1602.png"},
                {"title": "I2C address pads", "static_asset_path": "img/parts/display/i2c_address.jpg", "alt_text": "I2C address pads on LCD1602 backpack", "caption": "A0/A1/A2 pads can change the module address.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/i2c_address.jpg"},
                {"title": "Backlight and contrast controls", "static_asset_path": "img/parts/display/back_lcd1602.jpg", "alt_text": "LCD1602 backlight jumper and contrast potentiometer", "caption": "The jumper controls backlight; the potentiometer adjusts text contrast.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/back_lcd1602.jpg"},
            ],
            resources=[
                {"title": "SunFounder: I2C LCD1602", "url": f"{BASIC_SOURCE}component_i2clcd1602.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for pin labels, PCF8574 note, address pads, backlight, contrast, and images."},
                {"title": "Texas Instruments: PCF8574 datasheet", "url": "https://www.ti.com/lit/ds/symlink/pcf8574.pdf?ts=1627006546204&ref_url=https%253A%252F%252Fwww.google.com%252F", "resource_type": RT.DATASHEET, "notes": "Validated datasheet link for the PCF8574 I2C I/O expander."},
                {"title": "MicroPython: machine.I2C", "url": "https://docs.micropython.org/en/latest/library/machine.I2C.html", "resource_type": RT.LIBRARY, "notes": "Use to scan for the LCD address and communicate with the backpack."},
            ],
        )

        self.seed_component(
            slug="ws2812-neopixel-leds",
            defaults={
                "name": "WS2812 RGB 8 LEDs Strip",
                "category": "Display",
                "description": "An 8-pixel strip of individually addressable RGB LEDs. Each LED includes a WS2812B control IC inside the 5050 RGB package.",
                "how_it_is_used": "Students use it for animated light patterns, status bars, color effects, music-reactive lights, and IoT color indicators using one Pico data pin.",
                "signal_type": Component.SignalType.DIGITAL,
                "power_requirement": "SunFounder lists DC5V work voltage and 0.3W consumption per LED.",
                "pins": "Power, ground, and one data input line. Data flows through each pixel to the next.",
                "pinout_notes": "The WS2812 protocol sends 24-bit color data per pixel over one data wire. Pixel order and color channel order must match the driver expectations.",
                "datasheet_notes": "SunFounder identifies the LEDs as 5050RGB with built-in WS2812B IC. The WS2812B datasheet covers timing, voltage, current, and data protocol details.",
                "main_component": "WS2812B intelligent RGB LED in a 5050 package, identified by SunFounder.",
                "discrete_parts": "Eight WS2812B pixels on a flexible strip with adhesive backing.",
                "libraries": "Use MicroPython neopixel for pixel color control.",
                "voltage_notes": "The strip is a 5V part. Check power and data-level compatibility with the Pico before driving long or bright animations.",
                "safety_notes": "Full-white animations draw the most current. Power the strip appropriately and avoid overloading Pico power pins.",
                "common_mistakes": "Wrong data direction, no common ground, insufficient power, color channel order surprises, timing-sensitive code interruptions, and trying to run many LEDs at full brightness from the Pico alone.",
                "source_name": "SunFounder WS2812 RGB 8 LEDs Strip component page",
                "source_url": f"{BASIC_SOURCE}component_ws2812.html",
                "attribution": sf_component_source,
            },
            kits=[pico],
            assets=[
                {"title": "WS2812 RGB 8 LEDs strip", "static_asset_path": "img/parts/display/ws2812b.png", "alt_text": "WS2812 RGB 8 LEDs strip", "caption": "Eight individually addressable RGB LEDs controlled from one data line.", "source_name": sf_component_source, "source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/ws2812b.png"},
            ],
            resources=[
                {"title": "SunFounder: WS2812 RGB 8 LEDs Strip", "url": f"{BASIC_SOURCE}component_ws2812.html", "resource_type": RT.SUNFOUNDER, "notes": "Source page for strip features, WS2812B identification, and image."},
                {"title": "WS2812B datasheet", "url": "https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf", "resource_type": RT.DATASHEET, "notes": "Validated datasheet PDF link for WS2812B timing and electrical characteristics."},
                {"title": "MicroPython: neopixel", "url": "https://docs.micropython.org/en/latest/library/neopixel.html", "resource_type": RT.LIBRARY, "notes": "Use to control WS2812/NeoPixel-style LEDs from MicroPython."},
            ],
        )

        safety_items = [
            ("Pico GPIO is 3.3V", "Do not feed 5V signals into Raspberry Pi Pico 2 W GPIO pins."),
            ("Motors need drivers", "Do not power motors, pumps, or relays directly from GPIO pins."),
            ("Low-voltage relays only", "Beginner relay projects stay low-voltage DC only."),
            ("LiPo charging caution", "Battery charging needs careful setup and supervision."),
            ("Laser eye safety", "Never point a laser module at eyes or reflective surfaces."),
            ("Heartbeat sensor is educational", "Heartbeat modules are not medical devices."),
        ]
        for title, body in safety_items:
            SafetyWarning.objects.update_or_create(
                slug=slugify(title),
                defaults={"title": title, "body": body, "severity": "Medium", "published": True},
            )

        first_lesson, _ = LearningExperience.objects.update_or_create(
            code="001",
            defaults={
                "title": "Meet Your Pico 2 W",
                "slug": "meet-your-pico-2-w",
                "track": tracks[0],
                "content_type": LearningExperience.ContentType.CONCEPT,
                "difficulty": LearningExperience.Difficulty.BEGINNER,
                "estimated_time": "10-15 min",
                "main_skill": "Recognize the board, ports, pins, and 3.3V safety boundary",
                "prerequisites": "None. You only need the Pico 2 W board and a curious look at both sides.",
                "summary": "Meet the Raspberry Pi Pico 2 W before writing code: find the USB port, chip, wireless area, pins, power pins, and safe wiring rules.",
                "hook": "Before the Pico 2 W obeys your code, learn the tiny map printed on the board.",
                "student_outcome": "Student can point to the major parts of the Pico 2 W and explain why GPIO pins must stay 3.3V-safe.",
                "safety_level": LearningExperience.SafetyLevel.LOW,
                "status": LearningExperience.Status.PUBLISHED,
                "core_run_week": 1,
                "core_anchor": True,
                "a_la_carte": True,
                "optional_bonus": False,
                "recommended_after_core": False,
            },
        )
        first_lesson.required_kits.set([pico])
        first_lesson.required_components.set([Component.objects.get(slug="raspberry-pi-pico-2-w")])
        first_lesson.safety_warnings.set([SafetyWarning.objects.get(slug=slugify("Pico GPIO is 3.3V"))])
        CoreRunWeek.objects.get(week_number=1).anchor_learning_experiences.add(first_lesson)

        source_credit = "SunFounder Pico 2 W Starter Kit documentation, Getting to Know Pico 2 W, © 2026 SunFounder."
        lesson_sections = [
            {
                "order": 1,
                "title": "Mission: meet the board",
                "section_type": LearningExperienceSection.SectionType.TEXT,
                "body": (
                    "Today is a no-code scouting mission. Your job is to make the Pico 2 W feel less like a mystery rectangle and more like a tool you can name.\n\n"
                    "By the end, you should be able to pick up the board and find: the USB port, the main chip, the wireless area, the pin rows, the ground pins, and the 3.3V power pin.\n\n"
                    "Do not wire anything yet. This lesson is about knowing what you are holding before electricity gets involved."
                ),
            },
            {
                "order": 2,
                "title": "Board tour",
                "section_type": LearningExperienceSection.SectionType.MEDIA,
                "static_asset_path": "img/lessons/meet-your-pico-2-w/pico_2w_side.png",
                "static_asset_alt": "Side view of a Raspberry Pi Pico 2 W board",
                "static_asset_caption": "Use this image as a board-spotting guide. ",
                "static_asset_source_name": source_credit,
                "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/pico_2w_side.png",
                "body": (
                    "Look for these landmarks on your own board:\n\n"
                    "- USB port: the board's power and data doorway.\n"
                    "- BOOTSEL button: used during some setup and recovery steps.\n"
                    "- RP2350 chip: the brain that runs your MicroPython code later.\n"
                    "- Wireless hardware: what lets Pico 2 W join Wi-Fi and Bluetooth projects later.\n"
                    "- Two long pin rows: the places future circuits will connect.\n\n"
                    "Tiny check: hold your board so the USB port is at the top. Point to three things from the list before moving on."
                ),
            },
            {
                "order": 3,
                "title": "Pin map survival rules",
                "section_type": LearningExperienceSection.SectionType.SAFETY,
                "static_asset_path": "img/lessons/meet-your-pico-2-w/pico-2-w-pinout.png",
                "static_asset_alt": "Raspberry Pi Pico 2 W pinout diagram",
                "static_asset_caption": "Use the pinout as a map, not as decoration. ",
                "static_asset_source_name": source_credit,
                "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/pico-2-w-pinout.png",
                "body": (
                    "The pinout is your wiring map. You do not need to memorize it. You need to know how to read it.\n\n"
                    "Three rules matter right away:\n\n"
                    "1. GPIO pins are the general-purpose signal pins. They are for inputs and outputs.\n"
                    "2. GND means ground. Most circuits need a shared ground to behave.\n"
                    "3. Pico GPIO is 3.3V logic. Do not feed 5V signals into GPIO pins.\n\n"
                    "Some pins can do special jobs later, like analog input, I2C, SPI, UART, PWM, or power. For now, your power move is simple: check the pin label before plugging anything in."
                ),
            },
            {
                "order": 4,
                "title": "Board detective checkpoint",
                "section_type": LearningExperienceSection.SectionType.CHECKPOINT,
                "body": (
                    "Before you mark this lesson complete, do this no-code check:\n\n"
                    "- Point to the USB port.\n"
                    "- Point to BOOTSEL.\n"
                    "- Find one GND pin on the pinout.\n"
                    "- Find one GPIO pin on the pinout.\n"
                    "- Say out loud: GPIO pins need 3.3V-safe signals.\n\n"
                    "If you can do those five things, you are ready for the Thonny setup lesson."
                ),
            },
            {
                "order": 5,
                "title": "Private Dev Log",
                "section_type": LearningExperienceSection.SectionType.REFLECTION,
                "body": (
                    "Write two or three sentences:\n\n"
                    "1. One board part I can identify now is...\n"
                    "2. One pin-map rule I want to remember is...\n"
                    "3. One thing I want the Pico 2 W to do later is..."
                ),
            },
            {
                "order": 6,
                "title": "References and next step",
                "section_type": LearningExperienceSection.SectionType.TEXT,
                "body": (
                    "Reference used for board facts and images:\n"
                    "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/introduction_to_pico_2w.html\n\n"
                    "Original image sources copied into this project with visible attribution:\n"
                    "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/pico_2w_side.png\n"
                    "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/pico-2-w-pinout.png\n\n"
                    "Next lesson: Thonny IDE Introduction. That is where setup begins. This lesson stays no-code on purpose."
                ),
            },
        ]
        first_lesson.sections.exclude(order__in=[section["order"] for section in lesson_sections]).delete()
        for section in lesson_sections:
            LearningExperienceSection.objects.update_or_create(
                learning_experience=first_lesson,
                order=section["order"],
                defaults={
                    "title": section["title"],
                    "section_type": section["section_type"],
                    "body": section["body"],
                    "static_asset_path": section.get("static_asset_path", ""),
                    "static_asset_alt": section.get("static_asset_alt", ""),
                    "static_asset_caption": section.get("static_asset_caption", ""),
                    "static_asset_source_name": section.get("static_asset_source_name", ""),
                    "static_asset_source_url": section.get("static_asset_source_url", ""),
                    "published": True,
                },
            )

        pico_component = Component.objects.get(slug="raspberry-pi-pico-2-w")
        pico_safety = SafetyWarning.objects.get(slug=slugify("Pico GPIO is 3.3V"))

        thonny_credit = "SunFounder Pico 2 W Starter Kit documentation, Install and Introduce Thonny IDE, © 2026 SunFounder."
        self.seed_lesson(
            code="002",
            defaults={
                "title": "Install Thonny",
                "slug": "install-thonny",
                "track": tracks[0],
                "content_type": LearningExperience.ContentType.CONCEPT,
                "difficulty": LearningExperience.Difficulty.BEGINNER,
                "estimated_time": "15-25 min",
                "main_skill": "Install and recognize the Thonny IDE",
                "prerequisites": "You have met the Pico 2 W board and can find the USB port.",
                "summary": "Install Thonny, the editor students will use to write and run MicroPython on the Pico 2 W.",
                "hook": "Turn your computer into the place where Pico projects start.",
                "student_outcome": "Student installs Thonny and can identify the editor, shell, run button, stop button, save button, and interpreter selector.",
                "safety_level": LearningExperience.SafetyLevel.LOW,
                "status": LearningExperience.Status.PUBLISHED,
                "core_run_week": 1,
                "core_anchor": True,
                "a_la_carte": True,
                "optional_bonus": False,
                "recommended_after_core": False,
            },
            required_kits=[pico],
            required_components=[pico_component],
            safety_warnings=[],
            sections=[
                {
                    "order": 1,
                    "title": "Mission: install your code workshop",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "Thonny is where you will write tiny commands, save project files, and send code to the Pico 2 W.\n\n"
                        "In this lesson, your win is not a blinking light yet. Your win is opening the tool that will make the blinking light possible."
                    ),
                },
                {
                    "order": 2,
                    "title": "Download Thonny",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-thonny/download_thonny1.png",
                    "static_asset_alt": "Thonny website download area",
                    "static_asset_caption": "Pick the installer for your computer. ",
                    "static_asset_source_name": thonny_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/download_thonny1.png",
                    "body": (
                        "Open https://thonny.org/ and download the installer for your operating system.\n\n"
                        "If Thonny is already installed, open it and check the version. Pico 2 W support needs a modern Thonny, so update if your copy is old or missing Pico interpreter options."
                    ),
                },
                {
                    "order": 3,
                    "title": "If your computer warns you",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-thonny/install_thonny1.png",
                    "static_asset_alt": "Browser or Windows warning while downloading Thonny",
                    "static_asset_caption": "Installer warnings are a reason to check the source, not panic-click. ",
                    "static_asset_source_name": thonny_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/install_thonny1.png",
                    "body": (
                        "Some computers warn about new installers. Only continue if you downloaded Thonny from the official site.\n\n"
                        "If the file came from somewhere random, delete it and go back to https://thonny.org/."
                    ),
                },
                {
                    "order": 4,
                    "title": "Run the installer",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-thonny/install_thonny6.png",
                    "static_asset_alt": "Thonny installer ready to install",
                    "static_asset_caption": "The installer walks you through the setup. ",
                    "static_asset_source_name": thonny_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/install_thonny6.png",
                    "body": (
                        "Run the installer and follow the prompts.\n\n"
                        "On Windows, your browser or security tool might ask whether you want to keep or run the installer. Slow down, read the prompt, and make sure the file came from thonny.org before continuing."
                    ),
                },
                {
                    "order": 5,
                    "title": "Know the Thonny controls",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-thonny/thonny_ide1.jpg",
                    "static_asset_alt": "Annotated Thonny IDE interface",
                    "static_asset_caption": "You do not need every button yet; find the big ones first. ",
                    "static_asset_source_name": thonny_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/thonny_ide1.jpg",
                    "body": (
                        "Find these controls before moving on:\n\n"
                        "- Editor area: where your code will live.\n"
                        "- Shell: where quick messages and errors show up.\n"
                        "- Run button: starts the current script.\n"
                        "- Stop button: interrupts a running script.\n"
                        "- Save button: stores your file on the computer or Pico.\n"
                        "- Interpreter selector: chooses whether code runs as normal Python or MicroPython on the Pico."
                    ),
                },
                {
                    "order": 6,
                    "title": "Checkpoint",
                    "section_type": LearningExperienceSection.SectionType.CHECKPOINT,
                    "body": (
                        "Mark this complete when:\n\n"
                        "- Thonny opens on your computer.\n"
                        "- You can point to the editor and shell.\n"
                        "- You can find Run, Stop, Save, and the interpreter selector.\n\n"
                        "Do not worry if the Pico interpreter is not ready yet. That is the next lesson."
                    ),
                },
                {
                    "order": 7,
                    "title": "Private Dev Log",
                    "section_type": LearningExperienceSection.SectionType.REFLECTION,
                    "body": (
                        "Write two or three sentences:\n\n"
                        "1. My computer setup is...\n"
                        "2. One Thonny control I can find now is...\n"
                        "3. One setup issue I want to remember is..."
                    ),
                },
                {
                    "order": 8,
                    "title": "References and next step",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "Reference used for setup flow and screenshots:\n"
                        "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/pyproject/python_start/install_thonny.html\n\n"
                        "Next lesson: Install MicroPython on the Pico 2 W."
                    ),
                },
            ],
        )

        micropython_credit = "SunFounder Pico 2 W Starter Kit documentation, Install MicroPython on Your Pico 2 W, © 2026 SunFounder."
        self.seed_lesson(
            code="003",
            defaults={
                "title": "Install MicroPython on the Pico 2 W",
                "slug": "install-micropython-on-the-pico-2-w",
                "track": tracks[0],
                "content_type": LearningExperience.ContentType.SKILL_LAB,
                "difficulty": LearningExperience.Difficulty.BEGINNER,
                "estimated_time": "15-25 min",
                "main_skill": "Put the Pico 2 W into BOOTSEL mode and install MicroPython from Thonny",
                "prerequisites": "Thonny is installed and opens on your computer.",
                "summary": "Use Thonny to install MicroPython firmware so the Pico 2 W can run student code.",
                "hook": "Give the Pico 2 W the language it needs before asking it to do anything.",
                "student_outcome": "Student installs MicroPython on the Pico 2 W and can select the Pico MicroPython interpreter in Thonny.",
                "safety_level": LearningExperience.SafetyLevel.LOW,
                "status": LearningExperience.Status.PUBLISHED,
                "core_run_week": 1,
                "core_anchor": True,
                "a_la_carte": True,
                "optional_bonus": False,
                "recommended_after_core": False,
            },
            required_kits=[pico],
            required_components=[pico_component],
            safety_warnings=[],
            sections=[
                {
                    "order": 1,
                    "title": "Mission: teach the Pico its language",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "MicroPython is the version of Python that runs directly on the Pico 2 W.\n\n"
                        "This setup step puts MicroPython firmware onto the board. After this, Thonny can talk to the Pico instead of only running code on your computer."
                    ),
                },
                {
                    "order": 2,
                    "title": "Open Thonny first",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-micropython-pico-2-w/set_pico1.png",
                    "static_asset_alt": "Thonny window before Pico setup",
                    "static_asset_caption": "Start from Thonny so the install tool is ready. ",
                    "static_asset_source_name": micropython_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/set_pico1.png",
                    "body": "Open Thonny. Leave it open while you connect the Pico in the next step.",
                },
                {
                    "order": 3,
                    "title": "Enter BOOTSEL mode",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-micropython-pico-2-w/bootsel_onboard1.png",
                    "static_asset_alt": "BOOTSEL button on Pico 2 W",
                    "static_asset_caption": "BOOTSEL tells the board to appear as a setup drive. ",
                    "static_asset_source_name": micropython_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/bootsel_onboard1.png",
                    "body": (
                        "Unplug the Pico. Hold BOOTSEL, plug the USB cable into your computer, then release BOOTSEL after the board appears as a drive.\n\n"
                        "On many computers, the drive name starts with RPI. If it does not appear, try a different USB cable; charging-only cables are a common setup trap."
                    ),
                },
                {
                    "order": 4,
                    "title": "Choose Install MicroPython",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-micropython-pico-2-w/set_pico2.png",
                    "static_asset_alt": "Thonny interpreter menu with install MicroPython option",
                    "static_asset_caption": "The interpreter menu is in the lower-right area of Thonny. ",
                    "static_asset_source_name": micropython_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/set_pico2.png",
                    "body": (
                        "In Thonny, open the interpreter selector and choose the MicroPython install option.\n\n"
                        "If that option is missing, update Thonny and reconnect the Pico in BOOTSEL mode."
                    ),
                },
                {
                    "order": 5,
                    "title": "Pick the Pico 2 W target",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-micropython-pico-2-w/set_pico2w3.png",
                    "static_asset_alt": "Thonny MicroPython install dialog for Pico 2 W",
                    "static_asset_caption": "Choose the Pico 2 W variant, not a random board. ",
                    "static_asset_source_name": micropython_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/set_pico2w3.png",
                    "body": (
                        "Select the Pico 2 W or Pico 2 WH MicroPython variant. Confirm the target volume is the Pico drive, then install.\n\n"
                        "When installation finishes, the board may disconnect and reconnect. That is normal."
                    ),
                },
                {
                    "order": 6,
                    "title": "Confirm the install",
                    "section_type": LearningExperienceSection.SectionType.MEDIA,
                    "static_asset_path": "img/lessons/install-micropython-pico-2-w/set_pico2w4.png",
                    "static_asset_alt": "Thonny MicroPython install dialog after Pico 2 W selection",
                    "static_asset_caption": "A successful install gets the board ready for MicroPython scripts. ",
                    "static_asset_source_name": micropython_credit,
                    "static_asset_source_url": "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/_images/set_pico2w4.png",
                    "body": (
                        "Confirm the target and install. When the setup finishes, return to Thonny and select the Pico MicroPython interpreter.\n\n"
                        "If the board disappears for a moment, wait before unplugging. Firmware installs can cause a reconnect."
                    ),
                },
                {
                    "order": 7,
                    "title": "Checkpoint",
                    "section_type": LearningExperienceSection.SectionType.CHECKPOINT,
                    "body": (
                        "Mark this complete when:\n\n"
                        "- MicroPython has been installed from Thonny.\n"
                        "- Thonny can select a MicroPython interpreter for Raspberry Pi Pico.\n"
                        "- The Pico is connected with a data USB cable.\n\n"
                        "If Thonny cannot see the board, retry BOOTSEL mode and check the cable first."
                    ),
                },
                {
                    "order": 8,
                    "title": "Private Dev Log",
                    "section_type": LearningExperienceSection.SectionType.REFLECTION,
                    "body": (
                        "Write two or three sentences:\n\n"
                        "1. The easiest part of firmware setup was...\n"
                        "2. The confusing part was...\n"
                        "3. If the Pico is not detected later, I will check..."
                    ),
                },
                {
                    "order": 9,
                    "title": "References and next step",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "Reference used for setup flow and screenshots:\n"
                        "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/pyproject/python_start/install_micropython_to_pico.html\n\n"
                        "Next lesson: Blink the Built-in LED."
                    ),
                },
            ],
        )

        self.seed_lesson(
            code="004",
            defaults={
                "title": "Blink the Built-in LED",
                "slug": "blink-the-built-in-led",
                "track": tracks[0],
                "content_type": LearningExperience.ContentType.SKILL_LAB,
                "difficulty": LearningExperience.Difficulty.BEGINNER,
                "estimated_time": "15-25 min",
                "main_skill": "Run a MicroPython script that controls the Pico 2 W built-in LED",
                "prerequisites": "Thonny is installed, MicroPython is on the Pico 2 W, and Thonny can select the Pico interpreter.",
                "summary": "Run your first MicroPython hardware loop by blinking the Pico 2 W built-in LED.",
                "hook": "Make the board prove it is listening by blinking its own tiny light.",
                "student_outcome": "Student runs an original MicroPython script that toggles the Pico 2 W built-in LED.",
                "safety_level": LearningExperience.SafetyLevel.LOW,
                "status": LearningExperience.Status.PUBLISHED,
                "core_run_week": 1,
                "core_anchor": True,
                "a_la_carte": True,
                "optional_bonus": False,
                "recommended_after_core": False,
            },
            required_kits=[pico],
            required_components=[pico_component],
            safety_warnings=[pico_safety],
            sections=[
                {
                    "order": 1,
                    "title": "Mission: first visible proof",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "No breadboard yet. No loose wires yet. Your first hardware win uses the LED already built into the Pico 2 W.\n\n"
                        "You will run one small script, watch the board blink, then change the timing so the blink becomes yours."
                    ),
                },
                {
                    "order": 2,
                    "title": "Before you run",
                    "section_type": LearningExperienceSection.SectionType.SAFETY,
                    "body": (
                        "Check these first:\n\n"
                        "- Pico 2 W is connected with a data USB cable.\n"
                        "- Thonny is using the MicroPython interpreter for Raspberry Pi Pico.\n"
                        "- No jumper wires are connected to the board.\n"
                        "- You are only using the built-in LED, so there is no circuit to wire yet.\n\n"
                        "Reminder for future lessons: GPIO pins are 3.3V-safe only. Do not send 5V into GPIO."
                    ),
                },
                {
                    "order": 3,
                    "title": "Code: blink the built-in LED",
                    "section_type": LearningExperienceSection.SectionType.CODE,
                    "body": (
                        "from machine import Pin\n"
                        "from time import sleep\n\n"
                        "led = Pin(\"LED\", Pin.OUT)\n\n"
                        "while True:\n"
                        "    led.toggle()\n"
                        "    sleep(0.5)\n"
                    ),
                },
                {
                    "order": 4,
                    "title": "Run it in Thonny",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "Paste the code into a new Thonny file. Click Run.\n\n"
                        "If Thonny asks where to save the file, save it to the Pico or your computer with a clear name like blink_builtin_led.py.\n\n"
                        "The built-in LED should turn on and off about twice per second. Click Stop when you are done watching it."
                    ),
                },
                {
                    "order": 5,
                    "title": "What just happened",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "The line led = Pin(\"LED\", Pin.OUT) creates a handle for the built-in LED and sets it as an output.\n\n"
                        "Inside the loop, led.toggle() flips the LED to the opposite state. If it was off, it turns on. If it was on, it turns off.\n\n"
                        "sleep(0.5) pauses the loop so your eyes can see the change."
                    ),
                },
                {
                    "order": 6,
                    "title": "Debug it",
                    "section_type": LearningExperienceSection.SectionType.DEBUG,
                    "body": (
                        "If nothing blinks:\n\n"
                        "- Check that Thonny is connected to the Pico MicroPython interpreter.\n"
                        "- Check that you used a capital LED inside quotes.\n"
                        "- Click Stop, then Run again.\n"
                        "- Reconnect the board with a known data USB cable.\n\n"
                        "If you see an error, read the first line that mentions your code. The mistake is usually a missing quote, missing parenthesis, or indentation problem."
                    ),
                },
                {
                    "order": 7,
                    "title": "Remix: change the heartbeat",
                    "section_type": LearningExperienceSection.SectionType.REMIX,
                    "body": (
                        "Change sleep(0.5) to another number.\n\n"
                        "- 0.1 makes a fast blink.\n"
                        "- 1 makes a calm blink.\n"
                        "- 2 makes a slow signal.\n\n"
                        "Run after each change. Stop the script before editing again."
                    ),
                },
                {
                    "order": 8,
                    "title": "Checkpoint",
                    "section_type": LearningExperienceSection.SectionType.CHECKPOINT,
                    "body": (
                        "Mark this complete when:\n\n"
                        "- The built-in LED blinked from your code.\n"
                        "- You changed the blink speed at least once.\n"
                        "- You can explain what toggle and sleep do in your own words."
                    ),
                },
                {
                    "order": 9,
                    "title": "Private Dev Log",
                    "section_type": LearningExperienceSection.SectionType.REFLECTION,
                    "body": (
                        "Write two or three sentences:\n\n"
                        "1. My blink speed experiment was...\n"
                        "2. One error or almost-error I noticed was...\n"
                        "3. The next thing I want to control is..."
                    ),
                },
                {
                    "order": 10,
                    "title": "References and next step",
                    "section_type": LearningExperienceSection.SectionType.TEXT,
                    "body": (
                        "Reference used for the first LED-control idea:\n"
                        "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/pyproject/py_led.html\n\n"
                        "That SunFounder reference uses an external LED circuit. This ObsoleteHQ Week 1 lesson intentionally starts with the Pico 2 W built-in LED so the first code win needs no wiring."
                    ),
                },
            ],
        )

        for name, xp in [
            ("First Blink", 25),
            ("Setup Complete", 50),
            ("Debugging Hero", 25),
            ("Remix Maker", 40),
            ("Invention Shipper", 100),
        ]:
            Badge.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": f"Earned through real ObsoleteHQ progress: {name}.",
                    "reward_xp": xp,
                    "criteria_type": slugify(name),
                    "published": True,
                },
            )

        for title, symptom, checks, fixes in [
            ("LED does not turn on", "Your LED circuit stays dark.", "Check polarity, resistor, ground, and pin number.", "Flip the LED, move to the correct row, or test with a simpler blink."),
            ("Pico not detected", "Thonny cannot see the board.", "Check USB cable, boot mode, and selected interpreter.", "Try a data USB cable, reconnect while holding BOOTSEL, then select the right port."),
            ("Sensor values do not change", "The code runs but readings stay stuck.", "Check 3.3V, ground, signal pin, and raw value printout.", "Rewire one connection at a time and test raw values before thresholds."),
        ]:
            DebugCard.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "symptom": symptom,
                    "what_it_usually_means": "A wiring, pin, power, or setup assumption needs checking.",
                    "first_checks": checks,
                    "fixes": fixes,
                    "published": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded ObsoleteHQ structural data."))

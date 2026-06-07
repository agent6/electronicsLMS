<!-- Markdown planning document only. No application code, routes, templates, migrations, Docker files, or tutorial code. -->

# Responsive Design Spec

## Breakpoint Strategy

Design mobile-first. Add tablet and desktop layouts only when they improve scanning, comparison, or productivity.

## Mobile

- Bottom or compact navigation for core student routes.
- Tutorial pages use one readable column.
- Parts lists collapse into checklist groups.
- Safety notes appear before wiring instructions.
- Filters open in a sheet or stacked panel.
- Tables become cards.
- Touch targets are at least 44px.
- No horizontal scrolling for normal content.

## Tablet

- Tutorial content remains readable with side summary when space allows.
- Dashboard cards can use two columns.
- Admin lists become denser but remain touch usable.

## Desktop

- Tutorials can use a main reading column plus sticky progress/parts rail.
- Core Run map can show more stops at once.
- A la Carte filters can sit in a left rail.
- Admin dashboard can use tables, split panes, and bulk scanning.

## Fixed-Format Elements

Boards, progress maps, badges, icon buttons, and counters need stable dimensions so hover states, labels, and dynamic content do not shift layout.

## Media

Project writeups are text-only by product decision. Tutorial diagrams and images must be original assets once implementation reaches content authoring.

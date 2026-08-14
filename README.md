# MK11 Switch Moves

A mobile-first Progressive Web App for Mortal Kombat 11 on Nintendo Switch.

## Features

- All 38 source character entries, including the source's `Unannounced` entry.
- 1,595 structured move entries from the supplied MKKomplete Nintendo Switch source.
- Direction arrows instead of F/B/U/D in the interface.
- RIGHT / LEFT facing toggle that mirrors Forward and Back.
- Nintendo Switch-style controller visualisation.
- Simultaneous inputs versus sequential steps are represented separately.
- Practice / Loop mode with the current input highlighted.
- Offline-first PWA: the database is generated into `data/db.js` and cached by the service worker.

## Source

https://icemantraveler.github.io/mkksg/mk11/combos_switch.htm

The GitHub Pages workflow rebuilds the local database from the source and verifies that extraction produces 38 character entries and 1,595 moves.

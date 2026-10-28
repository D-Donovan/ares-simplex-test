# ARES simplex coverage test

A single-page logger and map for a simplex coverage test during an ARES net. Net control logs each
check-in's QTH and whether they can hear net control (and are heard) on the tactical simplex
frequencies, and the results appear as a color-coded map.

**Use it:** open the published page, enter your callsign and location, add the simplex frequencies,
and log stations as they report. The **Net control guide (PDF)** has a suggested script and a paper log sheet.

## Privacy

- This repository contains **no member data**: no callsign list, no locations, no logs.
- Everything you enter stays **in your own browser** (local storage) and is never uploaded. Use
  *Backup (JSON)* to save it, and *Clear all data* when finished.
- Pins are rounded to a 6-character grid square (a few miles) by default.
- The optional *Load member QTHs* button reads a CSV **from your own computer**; that file is not part
  of this repository and should stay private.

## Notes

- Needs internet for the map tiles (OpenStreetMap) and for the optional *Find address* lookup
  (OpenStreetMap Nominatim). Logging and exports work without it.
- Map: [Leaflet](https://leafletjs.com/). Not an official ARES form; adapt the procedure to your group's plan.

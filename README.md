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
- The only member information published here is `members-optin.csv`, and only for members who opted in.

## Shared map (opt-in only)

`members-optin.csv` lists members who **chose** to appear on the shared map. It contains **only**
`callsign,grid,agreed_on` (no names, addresses or other fields). The page loads it automatically and shows
those members as blue rings. Members join or leave by telling net control; see
[the opt-in sheet](ARES-Shared-Map-Opt-In.pdf). The file starts empty.

### Optional: APRS positions (private, local only)

Members can separately agree to let net control use their APRS position during a test. `aprs_snapshot.py`
(in this repo; it contains no keys) reads a **private** `aprs-optin.csv` and your own aprs.fi API key, asks
aprs.fi for just those callsign-SSIDs (usually one request), and writes `aprs-positions.json` with each position
**rounded to the member's chosen grid**, never exact coordinates. Load that file in the page. Those positions are
not published and the page does not keep them. Data courtesy of [aprs.fi](https://aprs.fi/).

## Notes

- Needs internet for the map tiles (OpenStreetMap) and for the optional *Find address* lookup
  (OpenStreetMap Nominatim). Logging and exports work without it.
- Map: [Leaflet](https://leafletjs.com/). Not an official ARES form; adapt the procedure to your group's plan.

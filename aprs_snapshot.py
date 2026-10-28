"""Snapshot APRS positions for members who agreed to it. Private: run on net control's computer only.

Reads aprs-optin.csv (callsign,aprs_ssid,precision,agreed_on), asks aprs.fi for just those callsign-SSIDs
(up to 20 per request, usually ONE request), and writes aprs-positions.json for the simplex-test page to load.

Privacy: by default exact latitude/longitude never reach the output file. Each position is rounded to the member's
chosen grid square (6 characters, or 4 if they asked for the coarser one). ONLY for a member whose precision is
"exact" in aprs-optin.csv (they explicitly chose it) does the file also hold their exact lat/lon. The file holds no
history and is replaced on every run. Do not publish it or commit it anywhere.

  py aprs_snapshot.py                      # uses aprs-optin.csv next to this script
  py aprs_snapshot.py --max-age-hours 3    # mark positions older than 3 h as stale
  py aprs_snapshot.py --apikey KEY         # or set APRSFI_API_KEY, or keep the key in ..\\aprs\\apikey.txt

Data courtesy of aprs.fi (https://aprs.fi/). Please keep that credit wherever the positions are shown.
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = 'https://api.aprs.fi/api/get'
UA = 'aprs-net-check/0.1 (+https://github.com/D-Donovan/aprs-olmsted-net-check)'
BATCH = 20
SSID_RE = re.compile(r'^[A-Z0-9]{3,7}(-\d{1,2})?$')


def grid6(lat, lon):
    lon += 180
    lat += 90
    A = 'ABCDEFGHIJKLMNOPQRSTUVWX'
    s = A[int(lon // 20)] + A[int(lat // 10)]
    lon %= 20
    lat %= 10
    s += str(int(lon // 2)) + str(int(lat))
    lon %= 2
    lat %= 1
    s += A[int(lon // (2 / 24))].lower() + A[int(lat // (1 / 24))].lower()
    return s


def find_key(arg):
    if arg:
        return arg.strip()
    if os.environ.get('APRSFI_API_KEY'):
        return os.environ['APRSFI_API_KEY'].strip()
    for p in (os.path.join(HERE, 'apikey.txt'), os.path.join(HERE, '..', 'aprs', 'apikey.txt')):
        if os.path.exists(p):
            return open(p, encoding='utf-8').read().strip()
    sys.exit('No aprs.fi API key found (use --apikey, APRSFI_API_KEY, or apikey.txt).')


def read_optin(path):
    if not os.path.exists(path):
        sys.exit('No %s yet. Export it from the page ("Export aprs-optin.csv") after members agree.' % os.path.basename(path))
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    out = []
    for r in rows:
        ssid = (r.get('aprs_ssid') or '').strip().upper()
        if not SSID_RE.match(ssid):
            print('Skipping a row with an invalid callsign-SSID:', repr(ssid))
            continue
        p = str(r.get('precision', '6')).strip().lower()
        prec = 'exact' if p in ('exact', 'x') else (4 if p == '4' else 6)
        out.append((re.sub(r'-\d+$', '', ssid), ssid, prec))
    return out


def fetch(names, key):
    q = urllib.parse.urlencode({'name': ','.join(names), 'what': 'loc', 'apikey': key, 'format': 'json'})
    req = urllib.request.Request(API + '?' + q, headers={'User-Agent': UA})
    j = json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace'))
    if j.get('result') != 'ok':
        sys.exit('aprs.fi said: %s (if it is a rate limit, wait a few minutes and try again)' % j.get('description', j))
    return j.get('entries', [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--optin', default=os.path.join(HERE, 'aprs-optin.csv'))
    ap.add_argument('--out', default=os.path.join(HERE, 'aprs-positions.json'))
    ap.add_argument('--apikey')
    ap.add_argument('--max-age-hours', type=float, default=6.0)
    a = ap.parse_args()

    members = read_optin(a.optin)
    if not members:
        sys.exit('Nobody to look up.')
    key = find_key(a.apikey)
    ssids = sorted({m[1] for m in members})
    found = {}
    for i in range(0, len(ssids), BATCH):
        for e in fetch(ssids[i:i + BATCH], key):
            found[str(e.get('name', '')).upper()] = e
        if i + BATCH < len(ssids):
            time.sleep(6)
    now = time.time()
    entries, missing = {}, []
    for base, ssid, prec in members:
        e = found.get(ssid)
        if not e or 'lat' not in e or 'lng' not in e:
            missing.append(ssid)
            continue
        lat, lng = float(e['lat']), float(e['lng'])
        g = grid6(lat, lng) if prec == 'exact' else grid6(lat, lng)[:prec]
        last, first = float(e.get('lasttime', 0)), float(e.get('time', 0))
        age_min = max(0, int((now - last) / 60))
        if base in entries and entries[base]['age_min'] <= age_min:
            continue                                    # same member listed twice: keep the freshest position
        entries[base] = {
            'ssid': ssid, 'grid': g, 'precision': prec, 'age_min': age_min,
            'speed_kmh': round(float(e.get('speed', 0) or 0), 1),
            'fixed_hours': round(max(0.0, (last - first) / 3600), 1),
            'stale': age_min > a.max_age_hours * 60,
        }
        if prec == 'exact':                              # only for members who chose exact; the grid above is still included
            entries[base]['lat'], entries[base]['lon'] = round(lat, 5), round(lng, 5)
    out = {'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'attribution': 'Data courtesy of aprs.fi', 'entries': entries}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print('Wrote %s: %d position(s), %d callsign-SSID(s) with no APRS position.' % (a.out, len(entries), len(missing)))
    for base, d in entries.items():
        print('  %-8s %-10s %-7s heard %4d min ago%s' % (base, d['ssid'], d['grid'], d['age_min'], '  (stale)' if d['stale'] else ''))
    if missing:
        print('  No position for:', ', '.join(missing))
    print('Data courtesy of aprs.fi.')


if __name__ == '__main__':
    main()

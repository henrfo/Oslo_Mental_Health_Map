"""
Builds assets/data/dps-oslo.geojson: the boundaries of the DPS catchment
areas listed in _data/dps.yml (run scripts/update_dps.py first).

Source: SSB's report "Opptaksområder for spesialisthelsetjenesten"
(https://statisticsnorway.github.io/speshelse/). SSB joins the KLASS DPS code
list to a grunnkrets map and merges the grunnkretser into DPS areas; the
report embeds the result as an interactive map. This script downloads the
report (~100 MB), takes the map under "DPS-enes opptaksområder", keeps the
areas named in _data/dps.yml, simplifies the outlines and writes GeoJSON.

Usage:  python3 scripts/update_dps_geo.py [path-to-downloaded-report.html]
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

REPORT_URL = 'https://statisticsnorway.github.io/speshelse/'
ROOT = Path(__file__).resolve().parent.parent
DPS_YML = ROOT / '_data' / 'dps.yml'
OUT = ROOT / 'assets' / 'data' / 'dps-oslo.geojson'
TOLERANCE = 0.0002   # simplification tolerance in degrees (~15–20 m)
PRECISION = 5        # decimal places kept (~1 m)

# Where to put the name for areas whose geometric centre lies far from where
# people live: Nydalen includes Marka (Nordmarka), Groruddalen includes Nittedal.
# [lon, lat]; checked to fall inside the area.
LABEL_OVERRIDES = {
    'Nydalen DPS': [10.775, 59.945],      # Sagene / Nordre Aker / Bjerke
    'Groruddalen DPS': [10.88, 59.94],    # Grorud / Stovner / Alna
}


def read_areas() -> list[dict]:
    """Minimal reader for the generated _data/dps.yml (no PyYAML needed)."""
    areas, current = [], None
    for line in DPS_YML.read_text(encoding='utf-8').splitlines():
        m = re.match(r'\s*-?\s*(code|dps|ssb_name|helseforetak|bydeler|outside_oslo):\s*(.*?)\s*$', line)
        if not m:
            continue
        key, value = m.groups()
        if key == 'code':
            current = {'code': value}
            areas.append(current)
        else:
            current[key] = json.loads(value)   # dps.yml writes JSON-style strings and lists
    return areas


def load_report(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding='utf-8', errors='replace')
    print(f'Downloading {REPORT_URL} …')
    with urllib.request.urlopen(REPORT_URL, timeout=300) as resp:
        return resp.read().decode('utf-8', errors='replace')


def dps_widget(report: str) -> dict:
    """The first map widget after the last 'DPS-enes opptaksområder' heading."""
    heading = report.rfind('DPS-enes opptaksområder</h3>')
    if heading < 0:
        sys.exit('Heading "DPS-enes opptaksområder" not found; the report layout may have changed')
    m = re.compile(r'<script type="application/json" data-for="[^"]+">(.*?)</script>', re.S).search(report, heading)
    if not m:
        sys.exit('No map widget found after the DPS heading')
    return json.loads(m.group(1))


def simplify(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Douglas–Peucker line simplification, iterative."""
    if len(points) < 4:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = points[a], points[b]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5 or 1e-12
        best, idx = 0.0, None
        for i in range(a + 1, b):
            x, y = points[i]
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def simplify_ring(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """A closed ring starts and ends on the same point, which gives Douglas–Peucker
    a zero-length baseline; split at the point farthest from the start instead."""
    if points[0] == points[-1]:
        points = points[:-1]
    x0, y0 = points[0]
    far = max(range(len(points)), key=lambda i: (points[i][0] - x0) ** 2 + (points[i][1] - y0) ** 2)
    first = simplify(points[:far + 1], tol)
    second = simplify(points[far:] + [points[0]], tol)
    return first + second[1:]


def label_point(ring: list[list[float]]) -> list[float]:
    """A point inside the ring for the area's name: the middle of the widest
    inside stretch along the line through the ring's centroid."""
    area = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        cross = x1 * y2 - x2 * y1
        area += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    cy /= 3 * area
    xs = sorted(x1 + (cy - y1) * (x2 - x1) / (y2 - y1)
                for (x1, y1), (x2, y2) in zip(ring, ring[1:])
                if (y1 <= cy < y2) or (y2 <= cy < y1))
    a, b = max(zip(xs[::2], xs[1::2]), key=lambda seg: seg[1] - seg[0])
    return [round((a + b) / 2, PRECISION), round(cy, PRECISION)]


def inside(point: list[float], ring: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon test."""
    x, y = point
    result = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            result = not result
    return result


def ring_to_coords(ring: dict) -> list[list[float]]:
    pts = simplify_ring(list(zip(ring['lng'], ring['lat'])), TOLERANCE)
    coords = [[round(x, PRECISION), round(y, PRECISION)] for x, y in pts]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def main() -> None:
    areas = read_areas()
    if not areas:
        sys.exit(f'No areas in {DPS_YML}; run scripts/update_dps.py first')

    widget = dps_widget(load_report(sys.argv[1] if len(sys.argv) > 1 else None))
    call = next(c for c in widget['x']['calls'] if c['method'] == 'addPolygons')
    polygons, popups = call['args'][0], call['args'][4]

    # Popups read "Opptaksområde: <name> / Befolkning: <n>"; dps.yml names end in " DPS"
    by_name = {}
    for poly, popup in zip(polygons, popups):
        m = re.match(r'Opptaksområde:\s*(.+?)\s*/\s*Befolkning:\s*([\d\s]+)', popup or '')
        if m:
            by_name[m.group(1)] = (poly, int(re.sub(r'\D', '', m.group(2))))

    features = []
    for area in areas:
        ssb_name = area.get('ssb_name') or re.sub(r'\s*DPS$', '', area['dps'])
        if ssb_name not in by_name:
            sys.exit(f'"{ssb_name}" from dps.yml not found in the SSB map')
        poly, population = by_name[ssb_name]
        coordinates = [[ring_to_coords(r) for r in part] for part in poly]
        largest = max((part[0] for part in coordinates), key=len)
        label = LABEL_OVERRIDES.get(area['dps']) or label_point(largest)
        if not any(inside(label, part[0]) for part in coordinates):
            sys.exit(f'Label point {label} for {area["dps"]} is outside the area')
        features.append({
            'type': 'Feature',
            'properties': {
                'code': area['code'],
                'dps': area['dps'],
                'helseforetak': area.get('helseforetak', ''),
                'population': population,
                'bydeler': area.get('bydeler', []),
                'outside_oslo': area.get('outside_oslo', []),
                'label': label,
            },
            'geometry': {
                'type': 'MultiPolygon',
                'coordinates': coordinates,
            },
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'type': 'FeatureCollection',
        'source': f'SSB, {REPORT_URL} (DPS-enes opptaksområder)',
        'features': features,
    }, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    points = sum(len(r) for f in features for part in f['geometry']['coordinates'] for r in part)
    print(f'Wrote {len(features)} areas, {points} points, {OUT.stat().st_size // 1024} KB to {OUT}')


if __name__ == '__main__':
    main()

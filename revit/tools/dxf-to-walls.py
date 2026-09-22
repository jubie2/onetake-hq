"""Polycam floor-plan DXF -> wall / opening / room / equipment JSON for the Revit build.

usage: dxf-to-walls.py <polycam.dxf> <polycam.csv> <out.json> [check.svg] [check.png]

Reads the layered DXF that Polycam exports (Poly-Walls, Poly-Doors, Poly-Windows,
Poly-Openings, Poly-Rooms, Poly-RoomLabels, Poly-Appliances, Poly-Fixtures, Poly-Furniture,
Poly-DimensionsExterior, Poly-Compass).  Units in the DXF are decimal feet.

Output coordinates: decimal feet, origin at the OUTER SW corner of the building bounding box,
X east / Y north IN PLAN ORIENTATION (the orientation Polycam drew).  True north is recorded
separately (compass heading of plan-up) so Revit's True North can be set; geometry is NOT
rotated so it can be checked against the Polycam PNG and the site photos as-is.

Walls: every Polycam wall is a 7-vertex rectangle of the global wall thickness (a Polycam
setting, 4" here).  Each one is collapsed to a centreline record in the close-shell.py shape
    {"dir":"H","y":..,"x0":..,"x1":..,"t":<in>,"len":..}
then merged along each line (touching pieces, and pieces separated by a door / window /
cased opening, become one wall; exterior and interior pieces are never merged with each
other), then snapped like tools/rationalize.py does (cluster, snap to the inch, anchor the
four outer faces) - but without rationalize's dedupe, which would drop touching collinear
walls.  A wall is EXTERIOR when one side of it has no room polygon (outside, or a void the
scanner never entered).  `revit_walls` is the same list in make_walls.py's {"type","a","b"}
shape.

Python 3, stdlib only (PIL optional, for the PNG).
"""
import sys, os, json, re, csv
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------- DXF reader
def _pairs(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\r\n') for l in f]
    for i in range(0, len(lines) - 1, 2):
        yield lines[i].strip(), lines[i + 1]

def read_dxf(path):
    pairs = list(_pairs(path))
    ents, i, n = [], 0, len(pairs)
    while i < n and not (pairs[i][0] == '2' and pairs[i][1].strip() == 'ENTITIES'):
        i += 1
    cur = None
    while i < n:
        c, v = pairs[i]; v = v.strip()
        if c == '0':
            if cur: ents.append(cur)
            if v == 'ENDSEC': cur = None; break
            cur = {'type': v, 'layer': None, 'pts': [], 'closed': 0, 'text': '', '_x': None}
        elif cur is not None:
            if c == '8': cur['layer'] = v
            elif c == '70' and cur['type'] == 'LWPOLYLINE': cur['closed'] = int(float(v)) & 1
            elif c == '10': cur['_x'] = float(v)
            elif c == '20' and cur['_x'] is not None:
                cur['pts'].append((cur['_x'], float(v))); cur['_x'] = None
            elif c in ('1', '3') and cur['type'] in ('MTEXT', 'TEXT'): cur['text'] += v
        i += 1
    for e in ents:
        e.pop('_x', None)
        if e['type'] in ('MTEXT', 'TEXT'):
            e['insert'] = e['pts'][0] if e['pts'] else None
            e['text'] = re.sub(r'\\[A-Za-z][^;]*;', '', e['text']).replace('\\P', ' ').replace('{', '').replace('}', '').strip()
    return ents

# ----------------------------------------------------------------------------- helpers
def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def ftin(v):
    """decimal feet -> 12'-3\" """
    sign = '-' if v < 0 else ''
    v = abs(v); f = int(v); i = int(round((v - f) * 12))
    if i == 12: f += 1; i = 0
    return "%s%d'-%d\"" % (sign, f, i)

def parse_ftin(s):
    m = re.match(r"\s*(\d+)'\s*(\d+)\"", s)
    return int(m.group(1)) + int(m.group(2)) / 12.0 if m else None

def point_in_poly(pt, poly):
    x, y = pt; inside = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi: inside = not inside
    return inside

def shoelace(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) / 2.0

# ----------------------------------------------------------------------------- main
def main(dxf, csvf, out, svg=None, png=None):
    ents = read_dxf(dxf)
    L = lambda layer, t=None: [e for e in ents if e['layer'] == layer and (t is None or e['type'] == t)]

    # ---- CSV: room facts + settings
    csv_rows = list(csv.reader(open(csvf, encoding='utf-8', errors='replace')))
    room_area, ceil_h, csv_items, settings = {}, {}, defaultdict(list), {}
    for r in csv_rows:
        if len(r) < 3: continue
        room, desc, val = r[0].strip(), r[1].strip(), r[2].strip()
        if desc.startswith('Floor area'): room_area[room] = float(val)
        elif desc.startswith('Ceiling height'): ceil_h[room] = parse_ftin(val)
        elif room == 'Settings': settings[desc] = val
        elif room == 'Entire Roomplan': settings[desc] = val
        m = re.match(r'(.+?) dimensions \(w x h x d\)', desc)
        if m:
            d = [parse_ftin(x) for x in val.split(' x ')]
            if len(d) == 3: csv_items[room].append({'kind': m.group(1).strip(), 'w': d[0], 'h': d[1], 'd': d[2]})
    wall_t_ft = parse_ftin(next((v for k, v in settings.items() if k.startswith('Wall thickness')), "0' 4\"")) or 4 / 12.0
    T_IN = round(wall_t_ft * 12, 1)
    compass = float(settings.get('Compass direction [deg]', 'nan'))

    # ---- origin: outer SW corner of the wall bbox
    wall_polys = [e['pts'] for e in L('Poly-Walls', 'LWPOLYLINE')]
    X0, Y0, X1, Y1 = bbox([p for pts in wall_polys for p in pts])
    W, H = X1 - X0, Y1 - Y0
    sh = lambda p: (p[0] - X0, p[1] - Y0)

    # ---- walls -> centrelines (raw)
    raw = []
    half = wall_t_ft / 2.0
    for pts in wall_polys:
        x0, y0, x1, y1 = bbox([sh(p) for p in pts])
        if (x1 - x0) >= (y1 - y0):   # horizontal
            raw.append({'dir': 'H', 'y': round((y0 + y1) / 2, 4), 'x0': round(x0 + half, 4), 'x1': round(x1 - half, 4), 't': T_IN})
        else:
            raw.append({'dir': 'V', 'x': round((x0 + x1) / 2, 4), 'y0': round(y0 + half, 4), 'y1': round(y1 - half, 4), 't': T_IN})
    for w in raw:
        w['len'] = round((w['x1'] - w['x0']) if w['dir'] == 'H' else (w['y1'] - w['y0']), 3)
    raw_pieces_total = sum(w['len'] + wall_t_ft for w in raw)   # Polycam counts each piece outer-to-outer

    # ---- room polygons (needed for the exterior test)
    room_polys = []
    for e in L('Poly-Rooms', 'LWPOLYLINE'):
        poly = [sh(p) for p in e['pts']]
        if poly[0] == poly[-1]: poly = poly[:-1]
        room_polys.append(poly)
    def in_any_room(pt): return any(point_in_poly(pt, poly) for poly in room_polys)
    # a wall is EXTERIOR when one side of it has no room (outside the building, or an unscanned void)
    for w in raw:
        off = half + 0.35
        if w['dir'] == 'H':
            mx = (w['x0'] + w['x1']) / 2; a, b = (mx, w['y'] + off), (mx, w['y'] - off)
        else:
            my = (w['y0'] + w['y1']) / 2; a, b = (w['x'] + off, my), (w['x'] - off, my)
        w['ext'] = not (in_any_room(a) and in_any_room(b))

    # ---- opening rectangles (needed before the merge: a gap spanned by an opening is one wall)
    def rects(layer):
        out = []
        for e in L(layer, 'LWPOLYLINE'):
            if len(e['pts']) != 5: continue
            x0, y0, x1, y1 = bbox([sh(p) for p in e['pts']])
            out.append((x0, y0, x1, y1))
        return out
    openings = []
    def add_opening(kind, x0, y0, x1, y1):
        w, h = x1 - x0, y1 - y0
        if w >= h:   # in a horizontal wall
            openings.append({'kind': kind, 'dir': 'H', 'y': round((y0 + y1) / 2, 3), 'a': round(x0, 3), 'b': round(x1, 3), 'w': round(w, 3)})
        else:
            openings.append({'kind': kind, 'dir': 'V', 'x': round((x0 + x1) / 2, 3), 'a': round(y0, 3), 'b': round(y1, 3), 'w': round(h, 3)})
    leaves = []
    for x0, y0, x1, y1 in rects('Poly-Doors'):
        if min(x1 - x0, y1 - y0) < 0.2: leaves.append((x0, y0, x1, y1)); continue   # open door leaf, not a jamb
        add_opening('door', x0, y0, x1, y1)
    for x0, y0, x1, y1 in rects('Poly-Windows'): add_opening('window', x0, y0, x1, y1)
    for x0, y0, x1, y1 in rects('Poly-Openings'): add_opening('opening', x0, y0, x1, y1)

    # ---- merge collinear pieces: Polycam splits a wall at every junction and every opening.
    # Join pieces on the same line when they touch (gap <= 0.5 ft) or when an opening spans the gap.
    def merged_walls(raw):
        def spanned(dirn, pos, lo, hi):
            for o in openings:
                if o['dir'] != dirn: continue
                opos = o['y'] if dirn == 'H' else o['x']
                if abs(opos - pos) <= 0.45 and o['a'] <= lo + 0.6 and o['b'] >= hi - 0.6: return True
            return False
        out = []
        for dirn in ('H', 'V'):
            pk, lo_k, hi_k = ('y', 'x0', 'x1') if dirn == 'H' else ('x', 'y0', 'y1')
            items = sorted([w for w in raw if w['dir'] == dirn], key=lambda w: (w[pk], w[lo_k]))
            groups = []
            for w in items:
                for g in groups:
                    if abs(g[pk] - w[pk]) <= 0.35 and g['ext'] == w['ext']:   # never merge ext with int
                        gap = w[lo_k] - g[hi_k]
                        if gap <= 0.5 or (gap < 8 and spanned(dirn, g[pk], g[hi_k], w[lo_k])):
                            g[hi_k] = max(g[hi_k], w[hi_k]); g[lo_k] = min(g[lo_k], w[lo_k]); g['n'] += 1
                            g[pk] = (g[pk] * (g['n'] - 1) + w[pk]) / g['n']
                            break
                else:
                    groups.append(dict(w, n=1))
            for g in groups:
                g.pop('n'); g['len'] = round(g[hi_k] - g[lo_k], 3); out.append(g)
        return out
    raw_pieces = len(raw)
    raw = merged_walls(raw)

    # ---- snap: same idea as tools/rationalize.py (cluster near-collinear lines, snap to the inch,
    # pull onto anchors) but WITHOUT its dedupe, which drops the shorter of two touching collinear
    # walls - fatal once exterior and interior pieces on one line are kept apart on purpose.
    INCH = 1 / 12.0
    snap_inch = lambda v: round(round(v / INCH) * INCH, 4)
    def cluster(vals, tol=0.35):
        vals = sorted(vals); groups = []
        for v in vals:
            if groups and v - groups[-1][-1] <= tol: groups[-1].append(v)
            else: groups.append([v])
        return {v: sum(g) / len(g) for g in groups for v in g}
    def anchor(v, anchors, tol=0.6):
        for a in anchors:
            if abs(v - a) <= tol: return a
        return v
    AX, AY = [half, W - half], [half, H - half]
    mapV = cluster([w['x'] for w in raw if w['dir'] == 'V']); mapH = cluster([w['y'] for w in raw if w['dir'] == 'H'])
    endsX = cluster([w['x0'] for w in raw if w['dir'] == 'H'] + [w['x1'] for w in raw if w['dir'] == 'H'] + [w['x'] for w in raw if w['dir'] == 'V'])
    endsY = cluster([w['y0'] for w in raw if w['dir'] == 'V'] + [w['y1'] for w in raw if w['dir'] == 'V'] + [w['y'] for w in raw if w['dir'] == 'H'])
    walls = []
    for w in raw:
        if w['dir'] == 'V':
            x = snap_inch(anchor(mapV[w['x']], AX)); y0 = snap_inch(anchor(endsY[w['y0']], AY)); y1 = snap_inch(anchor(endsY[w['y1']], AY))
            if abs(y1 - y0) < 0.8: continue
            walls.append({'dir': 'V', 'x': x, 'y0': min(y0, y1), 'y1': max(y0, y1), 't': w['t'], 'len': round(abs(y1 - y0), 2), 'ext': w['ext']})
        else:
            y = snap_inch(anchor(mapH[w['y']], AY)); x0 = snap_inch(anchor(endsX[w['x0']], AX)); x1 = snap_inch(anchor(endsX[w['x1']], AX))
            if abs(x1 - x0) < 0.8: continue
            walls.append({'dir': 'H', 'y': y, 'x0': min(x0, x1), 'x1': max(x0, x1), 't': w['t'], 'len': round(abs(x1 - x0), 2), 'ext': w['ext']})
    walls.sort(key=lambda w: (not w['ext'], -w['len']))
    for i, w in enumerate(walls): w['id'] = 'W%02d' % (i + 1)

    # ---- openings: host wall + swing + mark
    marks = {'door': 100, 'window': 0, 'opening': 200}
    for o in sorted(openings, key=lambda o: (o['kind'], o.get('y', 0), o.get('x', 0))):
        best = None
        opos = o['y'] if o['dir'] == 'H' else o['x']
        for w in walls:
            if w['dir'] != o['dir']: continue
            pos = w['y'] if w['dir'] == 'H' else w['x']
            lo, hi = (w['x0'], w['x1']) if w['dir'] == 'H' else (w['y0'], w['y1'])
            if abs(pos - opos) <= 0.45 and o['a'] >= lo - 0.6 and o['b'] <= hi + 0.6:
                d = abs(pos - opos)
                if best is None or d < best[0]: best = (d, w['id'])
        o['host'] = best[1] if best else None
        o['ext'] = bool(best) and next(w['ext'] for w in walls if w['id'] == best[1])
        if o['kind'] == 'door':
            o['swing'] = 'unknown'
            for lx0, ly0, lx1, ly1 in leaves:
                # leaf is a thin rect hinged at one jamb; it lies just off the wall line
                if o['dir'] == 'H':
                    near = (abs(lx0 - o['a']) < 0.3 or abs(lx1 - o['b']) < 0.3) and (abs(ly0 - opos) < 0.5 or abs(ly1 - opos) < 0.5)
                else:
                    near = (abs(ly0 - o['a']) < 0.3 or abs(ly1 - o['b']) < 0.3) and (abs(lx0 - opos) < 0.5 or abs(lx1 - opos) < 0.5)
                if near: o['swing'] = 'drawn (leaf %s)' % ftin(max(lx1 - lx0, ly1 - ly0))
        marks[o['kind']] += 1
        o['mark'] = ('%03d' % marks[o['kind']]) if o['kind'] != 'window' else ('%02d' % marks[o['kind']])
        o['w_ftin'] = ftin(o['w'])
    openings.sort(key=lambda o: (o['kind'], o['mark']))

    # ---- rooms (polygons are drawn to wall CENTRELINES; the CSV areas are net interior)
    labels = [(e['text'], sh(e['insert'])) for e in L('Poly-RoomLabels') if e.get('insert')]
    COMMERCIAL = {'Dining Room': 'DINING', 'Kitchen 1': 'PREP / BACK OF HOUSE', 'Kitchen 2': 'KITCHEN',
                  'Hallway': 'CORRIDOR', 'Bathroom 1': 'RESTROOM 1', 'Bathroom 2': 'RESTROOM 2',
                  'Other 1': 'STORAGE / OFFICE', 'Other 2': 'STORAGE', 'Other 3': 'CLOSET'}
    rooms = []
    for poly in room_polys:
        name = next((t for t, p in labels if point_in_poly(p, poly)), None)
        cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
        if not point_in_poly((cx, cy), poly):   # concave: use the label point instead
            lp = next((p for t, p in labels if t == name), None)
            if lp: cx, cy = lp
        rooms.append({'polycam_name': name, 'name': COMMERCIAL.get(name, name), 'area_sf_csv': room_area.get(name),
                      'area_sf_poly': round(shoelace(poly), 1), 'ceiling_ft': ceil_h.get(name),
                      'centroid': [round(cx, 2), round(cy, 2)], 'poly': [[round(x, 2), round(y, 2)] for x, y in poly]})
    rooms.sort(key=lambda r: -(r['area_sf_csv'] or 0))
    for i, r in enumerate(rooms): r['number'] = '%03d' % (101 + i)

    # ---- equipment: connected components of the line-art layers
    segs = []
    for lay in ('Poly-Appliances', 'Poly-Fixtures', 'Poly-Furniture'):
        for e in L(lay, 'LWPOLYLINE'):
            pts = [sh(p) for p in e['pts']]
            for a, b in zip(pts, pts[1:]): segs.append((lay, a, b))
    key = lambda p: (round(p[0] / 0.03), round(p[1] / 0.03))
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b): parent[find(a)] = find(b)
    for lay, a, b in segs: union(key(a), key(b))
    comps = defaultdict(list)
    for lay, a, b in segs: comps[find(key(a))].append((lay, a, b))
    # merge components whose bboxes overlap (Polycam draws sinks/cabinets as several loops)
    boxes = []
    for k, ss in comps.items():
        pts = [p for _, a, b in ss for p in (a, b)]
        boxes.append([list(bbox(pts)), ss[0][0], len(ss)])
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i][0], boxes[j][0]
                if a[0] <= b[2] + 0.05 and b[0] <= a[2] + 0.05 and a[1] <= b[3] + 0.05 and b[1] <= a[3] + 0.05 and boxes[i][1] == boxes[j][1]:
                    boxes[i][0] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    boxes[i][2] += boxes[j][2]; del boxes[j]; merged = True; break
            if merged: break
    equipment = []
    for (x0, y0, x1, y1), lay, nseg in boxes:
        w, d = x1 - x0, y1 - y0
        if max(w, d) < 0.4: continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        room = next((r for r in rooms if point_in_poly((cx, cy), r['poly'])), None)
        equipment.append({'layer': lay.replace('Poly-', ''), 'room': room['name'] if room else None,
                          'polycam_room': room['polycam_name'] if room else None,
                          'bbox': [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                          'w': round(w, 2), 'd': round(d, 2), 'center': [round(cx, 2), round(cy, 2)], 'kind': None})
    # label from the CSV item list, per room, best dimension match (w x d in plan, either orientation)
    for r in rooms:
        pool = list(csv_items.get(r['polycam_name'], []))
        cands = [q for q in equipment if q['polycam_room'] == r['polycam_name']]
        for q in sorted(cands, key=lambda q: -(q['w'] * q['d'])):
            best = None
            for it in pool:
                for a, b in ((it['w'], it['d']), (it['d'], it['w'])):
                    err = abs(a - q['w']) + abs(b - q['d'])
                    if err < 1.0 and (best is None or err < best[0]): best = (err, it)
            if best:
                q['kind'] = best[1]['kind']; q['csv_dims'] = '%s x %s x %s' % (ftin(best[1]['w']), ftin(best[1]['h']), ftin(best[1]['d']))
                pool.remove(best[1])
    for i, q in enumerate(sorted(equipment, key=lambda q: (q['room'] or '', -q['w'] * q['d']))): q['tag'] = 'E%02d' % (i + 1)
    equipment.sort(key=lambda q: q['tag'])

    # ---- printed exterior dimensions (for the sheet + verification)
    dims = [{'text': e['text'], 'ft': parse_ftin(e['text']), 'at': [round(v, 2) for v in sh(e['insert'])]}
            for e in L('Poly-DimensionsExterior') if e['type'] == 'MTEXT' and e.get('insert')]

    # ---- checks
    total_wall = sum(w['len'] for w in walls)
    net_wall = total_wall - sum(o['w'] for o in openings if o['host'])
    checks = {
        'bbox_ft': [round(W, 3), round(H, 3)], 'bbox_ftin': [ftin(W), ftin(H)],
        'printed_overall': [d['text'] for d in dims if d['ft'] and d['ft'] > 40],
        'wall_pieces_polycam': raw_pieces, 'wall_pieces_total_ft_outer': round(raw_pieces_total, 1),
        'wall_count_merged': len(raw), 'wall_count': len(walls), 'wall_count_ext': sum(1 for w in walls if w['ext']),
        'wall_total_ft': round(total_wall, 1), 'wall_total_less_openings_ft': round(net_wall, 1),
        'csv_wall_total': next((k.split('total wall length: ')[1].rstrip(')') for k in settings if 'total wall length' in k), None),
        'rooms': len(rooms), 'room_area_diff_pct': {r['name']: round(100 * (r['area_sf_poly'] - r['area_sf_csv']) / r['area_sf_csv'], 1) for r in rooms if r['area_sf_csv']},
        'openings': {k: sum(1 for o in openings if o['kind'] == k) for k in ('door', 'window', 'opening')},
        'openings_without_host': [o['kind'] + o['mark'] for o in openings if not o['host']],
        'equipment_components': len(equipment), 'equipment_labelled': sum(1 for q in equipment if q['kind']),
    }

    # ---- revit-ready wall list
    revit_walls = []
    for w in walls:
        typ = 'EXT %s' % ftin(wall_t_ft) if w['ext'] else 'Generic - %d"' % int(round(T_IN))
        a = [w['x0'], w['y']] if w['dir'] == 'H' else [w['x'], w['y0']]
        b = [w['x1'], w['y']] if w['dir'] == 'H' else [w['x'], w['y1']]
        revit_walls.append({'id': w['id'], 'type': typ, 'a': a, 'b': b, 'ext': w['ext']})

    result = {
        '_note': ('Polycam DXF -> feet. Origin = OUTER SW corner of the wall bbox in PLAN orientation (as Polycam '
                  'drew it; scan origin was at DXF (%.3f, %.3f)). X right, Y up on the plan. NOT rotated to true north: '
                  'plan-up has compass heading %.1f deg, i.e. true north is toward plan-LEFT; set Revit True North = '
                  '%.1f deg. Wall thickness %s is a Polycam SETTING applied to every wall, not a measurement; interior '
                  'faces are what the scanner measured, so exterior walls are almost certainly thicker than drawn - '
                  'the outer face is unverified. revit_walls types are placeholders: rename to the real WallType names '
                  'from GET /doc before /dev/run make_walls.py.') % (X0, Y0, compass, compass, ftin(wall_t_ft)),
        'source': {'dxf': os.path.basename(dxf), 'csv': os.path.basename(csvf), 'address_on_scan': settings.get('Address'),
                   'address_on_drawings': '2844 Main St #B, San Diego, CA', 'scan_date': '2026-09-18'},
        'true_north_heading_of_plan_up_deg': compass,
        'wall_thickness_setting_in': T_IN,
        'checks': checks,
        'dims_printed': dims,
        'walls': walls,
        'revit_walls': revit_walls,
        'openings': openings,
        'rooms': rooms,
        'equipment': equipment,
    }
    json.dump(result, open(out, 'w'), indent=1)
    print(json.dumps(checks, indent=1))
    if svg: write_svg(result, W, H, svg)
    if png: write_png(result, W, H, png)
    return result

# ----------------------------------------------------------------------------- check drawing
def write_svg(R, W, H, path):
    S = 10
    w_px, h_px = int(W * S) + 160, int(H * S) + 160
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-80 -80 %d %d" width="%d" height="%d" font-family="monospace" font-size="9">' % (w_px, h_px, w_px, h_px),
         '<rect x="-80" y="-80" width="%d" height="%d" fill="#fff"/>' % (w_px, h_px),
         '<!-- 10 px per foot; y flipped so plan-up is up. origin = outer SW corner of building. true north is to the LEFT (heading %.1f) -->' % R['true_north_heading_of_plan_up_deg'],
         '<g transform="translate(0,%d) scale(%d,-%d)">' % (int(H * S), S, S)]
    o.append('<!-- ROOMS -->')
    for r in R['rooms']:
        o.append('<polygon points="%s" fill="#f4f4f4" stroke="#bbb" stroke-width="0.05"/>' % ' '.join('%.2f,%.2f' % (x, y) for x, y in r['poly']))
    o.append('<!-- WALLS: black = exterior, blue = interior -->')
    for w in R['walls']:
        if w['dir'] == 'H': x1, y1, x2, y2 = w['x0'], w['y'], w['x1'], w['y']
        else: x1, y1, x2, y2 = w['x'], w['y0'], w['x'], w['y1']
        o.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"/> <!-- %s %s -->'
                 % (x1, y1, x2, y2, '#000' if w['ext'] else '#0057b8', w['t'] / 12.0, w['id'], ftin(w['len'])))
    o.append('<!-- OPENINGS: red = door, green = window, orange = cased opening -->')
    col = {'door': '#c00', 'window': '#090', 'opening': '#e80'}
    for op in R['openings']:
        if op['dir'] == 'H': x1, y1, x2, y2 = op['a'], op['y'], op['b'], op['y']
        else: x1, y1, x2, y2 = op['x'], op['a'], op['x'], op['b']
        o.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.5"/>' % (x1, y1, x2, y2, col[op['kind']]))
    o.append('<!-- EQUIPMENT bboxes -->')
    for q in R['equipment']:
        x0, y0, x1, y1 = q['bbox']
        o.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#999" stroke-width="0.08" stroke-dasharray="0.4,0.3"/>' % (x0, y0, x1 - x0, y1 - y0))
    o.append('</g>')
    o.append('<g fill="#000">')
    for r in R['rooms']:
        cx, cy = r['centroid']
        o.append('<text x="%d" y="%d" text-anchor="middle" font-weight="bold">%s %s</text>' % (int(cx * S), int(H * S - cy * S), r['number'], r['name']))
        o.append('<text x="%d" y="%d" text-anchor="middle" fill="#555">%s sf (%s)</text>' % (int(cx * S), int(H * S - cy * S) + 11, r['area_sf_csv'], r['polycam_name']))
    for op in R['openings']:
        x = (op['a'] + op['b']) / 2 if op['dir'] == 'H' else op['x']; y = op['y'] if op['dir'] == 'H' else (op['a'] + op['b']) / 2
        o.append('<text x="%d" y="%d" fill="%s" font-size="7">%s %s</text>' % (int(x * S) + 3, int(H * S - y * S) - 3, col[op['kind']], op['mark'], op['w_ftin']))
    for q in R['equipment']:
        if q['kind']:
            cx, cy = q['center']
            o.append('<text x="%d" y="%d" fill="#777" font-size="6" text-anchor="middle">%s</text>' % (int(cx * S), int(H * S - cy * S) + 2, q['kind']))
    o.append('</g>')
    o.append('<g fill="#c00" font-weight="bold">')
    for d in R['dims_printed']:
        x, y = d['at']
        o.append('<text x="%d" y="%d">%s</text>' % (int(x * S) - 12, int(H * S - y * S), d['text']))
    o.append('<text x="0" y="-60">%s  |  bbox %s x %s  |  %d walls %.0f ft  |  true north = LEFT (plan-up heading %.1f)</text>'
             % (R['source']['address_on_drawings'], R['checks']['bbox_ftin'][0], R['checks']['bbox_ftin'][1], R['checks']['wall_count'], R['checks']['wall_total_ft'], R['true_north_heading_of_plan_up_deg']))
    o.append('</g></svg>')
    open(path, 'w').write('\n'.join(o))

def write_png(R, W, H, path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print('PIL not available; skipped PNG'); return
    S = 24; M = 120
    im = Image.new('RGB', (int(W * S) + 2 * M, int(H * S) + 2 * M), 'white'); d = ImageDraw.Draw(im)
    P = lambda x, y: (M + x * S, M + (H - y) * S)
    for r in R['rooms']:
        d.polygon([P(x, y) for x, y in r['poly']], fill=(244, 244, 244), outline=(190, 190, 190))
    for q in R['equipment']:
        x0, y0, x1, y1 = q['bbox']; d.rectangle([P(x0, y1), P(x1, y0)], outline=(170, 170, 170))
    for w in R['walls']:
        a = P(w['x0'], w['y']) if w['dir'] == 'H' else P(w['x'], w['y0']); b = P(w['x1'], w['y']) if w['dir'] == 'H' else P(w['x'], w['y1'])
        d.line([a, b], fill=(0, 0, 0) if w['ext'] else (0, 87, 184), width=max(2, int(w['t'] / 12 * S)))
    col = {'door': (200, 0, 0), 'window': (0, 150, 0), 'opening': (230, 130, 0)}
    for op in R['openings']:
        a = P(op['a'], op['y']) if op['dir'] == 'H' else P(op['x'], op['a']); b = P(op['b'], op['y']) if op['dir'] == 'H' else P(op['x'], op['b'])
        d.line([a, b], fill=col[op['kind']], width=8)
        x = (op['a'] + op['b']) / 2 if op['dir'] == 'H' else op['x']; y = op['y'] if op['dir'] == 'H' else (op['a'] + op['b']) / 2
        px, py = P(x, y); d.text((px + 5, py - 14), '%s %s' % (op['mark'], op['w_ftin']), fill=col[op['kind']])
    for r in R['rooms']:
        px, py = P(*r['centroid']); d.text((px - 30, py - 8), '%s %s' % (r['number'], r['name']), fill=(0, 0, 0)); d.text((px - 30, py + 4), '%s sf' % r['area_sf_csv'], fill=(90, 90, 90))
    for q in R['equipment']:
        if q['kind']: px, py = P(*q['center']); d.text((px - 12, py - 4), q['kind'], fill=(120, 120, 120))
    for dm in R['dims_printed']:
        px, py = P(*dm['at']); d.text((px - 14, py - 6), dm['text'], fill=(200, 0, 0))
    d.text((M, 30), '%s | bbox %s x %s | true north = LEFT' % (R['source']['address_on_drawings'], R['checks']['bbox_ftin'][0], R['checks']['bbox_ftin'][1]), fill=(0, 0, 0))
    im.save(path)

if __name__ == '__main__':
    if len(sys.argv) < 4: print(__doc__); sys.exit(1)
    main(*sys.argv[1:6])

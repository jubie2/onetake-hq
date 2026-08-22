# Numbered keynote bubbles for elevations / plans, matching each sheet's legend.
# Drawn (leader + 2 arcs + number) because this project's keynote table is Revit's stock
# CSI list and the office uses hand-numbered User keynotes, which the API cannot create.
# args {"group":"elev","dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId, CurveElement,
                               TextNote, TextNoteOptions, TextNoteType, HorizontalTextAlignment,
                               BuiltInParameter as BIP, XYZ as _XYZ, Line, Arc, Wall)
from System.Collections.Generic import List
import math
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
R = 0.55
dry = args.get('dry', True)
# (number, matcher key) - matcher keys are resolved below
GROUPS = {
 'elev': (['ADU - North Elevation', 'ADU - South Elevation',
           'ADU - East Elevation', 'ADU - West Elevation'],
          [('1', 'roof'), ('3', 'louver'), ('2', 'window'), ('4', 'stucco'), ('6', 'extdoor')]),
 'plan': (['ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'],
          [('1', 'perimdoor'), ('2', 'toilet')]),
}
grp = args.get('group', 'elev')
VIEWS, SPEC = GROUPS[grp]
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
def famname(e):
    try: return e.Symbol.Family.Name
    except Exception: return ''
L = []
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None:
        L.append('%s NOT FOUND' % nm); continue
    bb = v.CropBox; tfm = bb.Transform; inv = tfm.Inverse
    items = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else ''
            if cn not in ('Roofs', 'Walls', 'Windows', 'Doors', 'Generic Models',
                          'Plumbing Fixtures'): continue
            b = e.get_BoundingBox(None)
            if b is None: continue
            c = _XYZ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0,
                     (b.Min.Z + b.Max.Z) / 2.0)
            if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
            q = inv.OfPoint(c)                       # X across, Y up, Z depth
            if not (bb.Min.X + 0.5 <= q.X <= bb.Max.X - 0.5): continue
            if not (bb.Min.Y + 0.5 <= q.Y <= bb.Max.Y - 0.5): continue
            ext = False
            if isinstance(e, Wall):
                try: ext = str(e.WallType.Function) == 'Exterior'
                except Exception: pass
            elif cn in ('Doors', 'Windows'):
                try:                                   # is it in an exterior wall?
                    h = e.Host
                    ext = isinstance(h, Wall) and str(h.WallType.Function) == 'Exterior'
                except Exception: pass
            perim = min(abs(c.X - 1157.9), abs(c.X - 1186.5),
                        abs(c.Y + 150.3), abs(c.Y + 125.7))
            items.append({'cat': cn, 'x': q.X, 'y': q.Y, 'd': abs(q.Z), 'perim': perim,
                          'fam': famname(e), 'ext': ext,
                          'w': b.Max.X - b.Min.X, 'h': b.Max.Z - b.Min.Z})
        except Exception: pass
    walls = [i for i in items if i["cat"] == "Walls"]
    nearD = min([i["d"] for i in walls]) if walls else 0.0
    # only key what is on the face we are looking at - meaningless in a plan view
    LIMIT = (nearD + 3.0) if grp == 'elev' else 1e9
    def near(pred):
        c = [i for i in items if pred(i) and i["d"] <= LIMIT]
        if not c: return None
        c.sort(key=lambda i: i["d"])
        return c[0]
    facew = [i for i in walls if i["d"] <= LIMIT]
    def blankwall():
        if not facew: return None
        xs = [i["x"] for i in facew]; ys = [i["y"] for i in facew]
        return {"x": min(xs) + (max(xs) - min(xs)) * 0.25 - 4.0,
                "y": min(ys) - 3.0, "d": nearD}
    M = {
      # a roof spans the whole depth, so it is exempt from the near-face filter
      'roof':    lambda: (sorted([i for i in items if i['cat'] == 'Roofs'],
                                 key=lambda i: i['d']) or [None])[0],
      'louver':  lambda: near(lambda i: i['cat'] == 'Generic Models' and
                              ('louver' in i['fam'].lower() or 'vent' in i['fam'].lower())),
      'window':  lambda: near(lambda i: i['cat'] == 'Windows' and i['h'] > 2.5),
      "stucco":  blankwall,
      'extdoor': lambda: near(lambda i: i['cat'] == 'Doors' and i['ext'] and i['w'] > 2.4),
      'toilet':  lambda: near(lambda i: i['cat'] == 'Plumbing Fixtures'),
      # no ADU door is hosted in a perimeter wall, so key the one closest to it
      'perimdoor': lambda: (sorted([i for i in items if i['cat'] == 'Doors' and i['w'] > 2.4],
                                   key=lambda i: i['perim']) or [None])[0],
    }
    jobs = []; miss = []
    for num, key in SPEC:
        hit = M[key]()
        if hit is None: miss.append('%s/%s' % (num, key)); continue
        jobs.append((num, hit['x'], hit['y'], key))
    L.append('%-24s %d bubbles %s   missing: %s' % (
        nm, len(jobs), ','.join('%s@%s' % (j[0], j[3]) for j in jobs), miss or '-'))
    if dry: continue
    t = Transaction(doc, 'OneTake: %s bubbles' % grp); _prep(t); t.Start()
    def W(x, y): return tfm.OfPoint(_XYZ(x, y, 0.0))
    n = 0
    used = []
    for i, (num, tx, ty, key) in enumerate(jobs):
        # park the bubble just clear of its target, flipping if it would leave the crop
        bx, by = tx + 3.0, ty + 2.2
        if bx > bb.Max.X - 1.2: bx = tx - 3.0
        if by > bb.Max.Y - 1.2: by = ty - 2.2
        for ux, uy in used:                       # nudge apart if two land together
            if abs(bx - ux) < 1.4 and abs(by - uy) < 1.4: by = uy - 1.8
        used.append((bx, by))
        try:
            doc.Create.NewDetailCurve(v, Line.CreateBound(W(tx, ty), W(bx - R, by)))
            c = W(bx, by)
            xa = (W(bx + 1, by) - c).Normalize(); ya = (W(bx, by + 1) - c).Normalize()
            doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
            doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
            o = TextNoteOptions(tt.Id)
            o.HorizontalAlignment = HorizontalTextAlignment.Center
            TextNote.Create(doc, v.Id, W(bx, by + 0.28), num, o)
            n += 1
        except Exception as ex:
            L.append('    %s fail %s' % (num, str(ex)[:45]))
    doc.Regenerate(); t.Commit()
    L.append('    placed %d' % n)
result = '\n'.join(L)

# Draw the mechanical devices on both ADU mech plans (mini-splits, condenser,
# exhaust fans, thermostat, hoods, duct runs + terminations, IAQ fan), place the
# smoke / CO symbols, then keynote-tag every one of them with a real leader.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol, ElementId,
                               XYZ as _XYZ, Line, Arc, GraphicsStyle, TextNote,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
CENX, CENY = 1157.520, 104.867
def PT(x, y): return _XYZ(x, y, 0)
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
sd_sym = doc.GetElement(ElementId(1027474))   # Smoke :: Smoke Detector[1]
co_sym = doc.GetElement(ElementId(1027472))   # Smoke :: CARBONMONOXIDE
# ---- device schedules: (keynote, kind, x, y [, x2, y2 for ducts]) ----
F1 = [
 ('1',  'sq',   1146.0, 101.0),                      # thermostat
 ('2',  'ms',   1151.0, 104.0), ('2', 'ms', 1135.5, 108.5), ('2', 'ms', 1137.5, 92.5),
 ('3',  'cu',   1171.1, 92.1),                       # condensing unit on pad
 ('4',  'ef',   1143.0, 110.5), ('4', 'ef', 1147.4, 92.8),
 ('5',  'duct', 1169.0, 114.7, 1167.5, 120.6),       # dryer duct
 ('6',  'term', 1167.5, 120.6),
 ('7',  'hood', 1164.2, 114.9),                      # kitchen hood
 ('8',  'duct', 1164.2, 114.9, 1163.0, 119.5),
 ('9',  'term', 1163.0, 119.5),
 ('10', 'none', 1174.9, 119.0),                      # WH P&T line
 ('11', 'none', 1174.4, 117.9),                      # heat-pump WH (real family)
 ('12', 'sd',   1135.8, 106.0), ('12', 'sd', 1138.2, 92.0), ('12', 'sd', 1143.5, 101.5),
 ('13', 'co',   1144.8, 102.8),
 ('14', 'iaq',  1150.5, 95.0),
]
F2 = [
 ('1',  'sq',   1157.0, 101.5),
 ('2',  'ms',   1160.5, 104.5), ('2', 'ms', 1138.5, 108.5), ('2', 'ms', 1140.5, 93.5),
 ('4',  'ef',   1146.0, 111.5), ('4', 'ef', 1149.1, 92.8),
 ('5',  'duct', 1178.9, 106.9, 1185.0, 108.5),
 ('6',  'term', 1185.0, 108.5),
 ('7',  'hood', 1178.6, 115.5),
 ('8',  'duct', 1178.6, 115.5, 1177.4, 120.1),
 ('9',  'term', 1177.4, 120.1),
 ('10', 'none', 1181.1, 120.4),
 ('11', 'none', 1180.6, 119.3),
 ('12', 'sd',   1138.5, 107.0), ('12', 'sd', 1141.0, 93.5), ('12', 'sd', 1146.5, 102.5),
 ('13', 'co',   1147.6, 103.6),
 ('14', 'iaq',  1152.0, 97.0),
]
JOBS = [(2244930, F1), (2244778, F2)]
L = []
t = Transaction(doc, 'OneTake: mech devices'); _prep(t); t.Start()
for s2 in (sym, sd_sym, co_sym):
    if s2 is not None and not s2.IsActive: s2.Activate()
doc.Regenerate()
for vid, sched in JOBS:
    v = doc.GetElement(ElementId(vid))
    kill = []
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name in ('TAG LABEL', 'Smoke'): kill.append(e.Id)
        except Exception: pass
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType():
        if e.OwnerViewId == v.Id: kill.append(e.Id)
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    def dline(x0, y0, x1, y1, dashed=False):
        try:
            ce = doc.Create.NewDetailCurve(v, Line.CreateBound(PT(x0, y0), PT(x1, y1)))
            if dashed and dash:
                try: ce.LineStyle = dash
                except Exception: pass
        except Exception as ex:
            L.append('  line fail %s' % str(ex)[:40])
    def drect(cx, cy, w, h):
        hw, hh = w / 2.0, h / 2.0
        c = [(cx + UX * sx * hw + VX * sy * hh, cy + UY * sx * hw + VY * sy * hh)
             for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for i in range(4):
            dline(c[i][0], c[i][1], c[(i + 1) % 4][0], c[(i + 1) % 4][1])
    def dcirc(cx, cy, r):
        for a0, a1 in ((0.0, math.pi), (math.pi, 2 * math.pi)):
            try:
                arc = Arc.Create(PT(cx, cy), r, a0, a1, _XYZ(1, 0, 0), _XYZ(0, 1, 0))
                doc.Create.NewDetailCurve(v, arc)
            except Exception as ex:
                L.append('  arc fail %s' % str(ex)[:40])
    nd = 0
    for row in sched:
        kn, kind = row[0], row[1]
        x, y = row[2], row[3]
        if kind == 'sq':    drect(x, y, 0.7, 0.7); nd += 1
        elif kind == 'ms':  drect(x, y, 3.0, 0.9); nd += 1
        elif kind == 'cu':  drect(x, y, 3.0, 2.2); nd += 1
        elif kind == 'hood': drect(x, y, 2.6, 1.9); nd += 1
        elif kind == 'ef':  dcirc(x, y, 0.55); dline(x - 0.39, y - 0.39, x + 0.39, y + 0.39); nd += 1
        elif kind == 'iaq': dcirc(x, y, 0.65); dline(x - 0.46, y - 0.46, x + 0.46, y + 0.46); nd += 1
        elif kind == 'term': dcirc(x, y, 0.4); nd += 1
        elif kind == 'duct':
            dline(x, y, row[4], row[5], True); nd += 1
        elif kind in ('sd', 'co'):
            try:
                doc.Create.NewFamilyInstance(PT(x, y), sd_sym if kind == 'sd' else co_sym, v)
                nd += 1
            except Exception as ex:
                L.append('  %s fail %s' % (kind, str(ex)[:40]))
    doc.Regenerate()
    # keynote tags: sit 3 ft outward from the building centre, leader onto the device
    placed = []
    for row in sched:
        kn, kind = row[0], row[1]
        if kind == 'duct':
            tx, ty = (row[2] + row[4]) / 2.0, (row[3] + row[5]) / 2.0
        else:
            tx, ty = row[2], row[3]
        dx, dy = tx - CENX, ty - CENY
        m = math.hypot(dx, dy) or 1.0
        ox, oy = tx + dx / m * 3.2, ty + dy / m * 3.2
        try:
            fi = doc.Create.NewFamilyInstance(PT(ox, oy), sym, v)
            p = fi.LookupParameter('TEXT')
            if p: p.Set(kn)
            doc.Regenerate()
            e2 = doc.GetElement(fi.Id)
            try:
                e2.addLeader(); doc.Regenerate()
                lds = list(e2.GetLeaders())
                if lds:
                    lds[-1].End = PT(tx, ty)
                    try: lds[-1].Elbow = PT(tx + dx / m * 1.6, ty + dy / m * 1.6)
                    except Exception: pass
            except Exception: pass
            placed.append((fi.Id, kn))
        except Exception as ex:
            L.append('  tag %s fail %s' % (kn, str(ex)[:40]))
    doc.Regenerate()
    for eid, kn in placed:
        p2 = doc.GetElement(eid).LookupParameter('TEXT')
        if p2 and p2.AsString() != kn: p2.Set(kn)
    L.append('%s: %d devices drawn, %d keynotes' % (v.Name, nd, len(placed)))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

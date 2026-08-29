# Keynote-tag the re-cut views.  Targets are real elements / real points inside the
# footprint (s in [-31,27], t in [-7,20.5]); tag parks at the paper edge on the same
# side as its target so no leader crosses the building.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               ElementId, XYZ as _XYZ, BuiltInCategory as BIC)
from System.Collections.Generic import List
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
BX, BY = 1161.1251, 98.8210
CX = BX + UX * (-2.0) + VX * 6.75
CY = BY + UY * (-2.0) + VY * 6.75
def P(s, t, z):
    return (CX + UX * s + VX * t, CY + UY * s + VY * t, z)
# view id: (origin world, halfwidth, [(keynote, target, tag z)])
JOBS = {
 2245246: ((1152.64, 124.01), 33.0, [                       # North elevation
    ('2', (1135.5, 112.5, 14.67), 18.5), ('4', P(-14.0, 19.57, 9.0), 9.5),
    ('5', (1148.2, 115.7, 7.17), 5.0),   ('6', (1152.6, 116.8, 3.5), 1.5),
    ('2', (1160.8, 118.9, 14.67), 20.5), ('1', P(6.0, 19.57, 24.5), 26.5),
    ('8', (1180.4, 116.0, 19.0), 15.5)]),
 2245255: ((1162.40, 85.73), 33.0, [                        # South elevation
    ('7', (1185.8, 98.8, 3.5), 6.0),     ('8', (1168.0, 91.2, 9.0), 13.0),
    ('6', (1152.2, 92.4, 3.5), 1.5),     ('5', (1150.4, 89.8, 7.17), 8.5),
    ('2', (1157.6, 91.7, 3.67), 4.0),    ('2', (1149.5, 89.6, 17.17), 19.5),
    ('4', P(-22.0, -6.06, 9.0), 10.0),   ('1', P(6.0, -6.06, 24.5), 26.5)]),
 2245264: ((1191.44, 113.51), 20.0, [                       # East elevation
    ('1', P(25.0, 6.0, 24.5), 26.5),     ('3', P(22.0, -5.0, 20.8), 21.5),
    ('6', (1182.2, 119.7, 13.5), 14.5),  ('5', (1182.0, 107.3, 18.17), 18.5),
    ('4', P(25.5, 14.0, 6.0), 6.5),      ('7', (1185.8, 98.8, 3.5), 2.0)]),
 2245273: ((1123.60, 96.22), 20.0, [                        # West elevation
    ('1', P(-30.0, 6.0, 24.5), 26.5),    ('2', (1129.4, 100.8, 3.17), 4.5),
    ('2', (1134.3, 91.9, 14.67), 16.0),  ('4', P(-30.2, 14.0, 9.0), 9.5)]),
 2245282: ((1138.14, 99.93), 20.0, [                        # Section 1 (cut s=-20)
    ('1', P(-20, 6, 22.9), 27.0),   ('11', P(-20, 14, 22.0), 24.5),
    ('9', P(-20, 0, 22.3), 24.0),   ('7', P(-20, 18, 20.8), 20.5),
    ('4', P(-20, 17, 16.0), 16.5),  ('10', P(-20, -4, 16.0), 17.0),
    ('8', P(-20, -5, 6.5), 8.5),    ('2', P(-20, 19.3, 6.0), 6.0),
    ('9', P(-20, 6, 11.4), 12.0),   ('6', P(-20, 18, 1.0), 2.0),
    ('5', P(-20, -5, 1.5), 3.5),    ('3', P(-20, 6, 0.5), -1.0),
    ('12', P(-20, -5.5, -1.0), -2.5)]),
 2245291: ((1174.96, 109.31), 20.0, [                       # Section 2 (cut s=+18)
    ('1', P(18, 6, 22.9), 27.0),    ('9', P(18, 12, 22.3), 24.0),
    ('4', P(18, -4, 16.0), 17.0),   ('2', P(18, 19.3, 6.0), 6.0),
    ('8', P(18, -5, 6.5), 9.0),     ('3', P(18, 6, 0.5), -1.0),
    ('12', P(18, -5.5, -1.0), -2.5)]),
 2245300: ((1154.80, 115.53), 33.0, [                       # Section 3 (cut t=+11)
    ('1', P(0, 11, 22.9), 27.0),    ('11', P(-12, 11, 22.0), 24.5),
    ('9', P(10, 11, 22.3), 24.0),   ('7', P(-25, 11, 20.8), 20.5),
    ('4', P(15, 11, 16.0), 16.5),   ('10', P(-28, 11, 15.5), 17.0),
    ('2', P(-30, 11, 6.0), 6.0),    ('8', P(20, 11, 6.5), 9.0),
    ('6', P(-29, 11, 1.0), 2.0),    ('5', P(24, 11, 1.5), 3.5),
    ('3', P(0, 11, 0.5), -1.0),     ('12', P(-20, 11, -1.0), -2.5)]),
 2245309: ((1158.26, 101.96), 33.0, [                       # Section 4 (cut t=-3)
    ('1', P(0, -3, 22.9), 27.0),    ('9', P(-10, -3, 22.3), 24.0),
    ('4', P(12, -3, 16.0), 16.5),   ('2', P(-30, -3, 6.0), 6.0),
    ('8', P(20, -3, 6.5), 9.0),     ('3', P(0, -3, 0.5), -1.0),
    ('12', P(18, -3, -1.0), -2.5)]),
}
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
L = []
t = Transaction(doc, 'OneTake: retag re-cut v2'); _prep(t); t.Start()
if not sym.IsActive: sym.Activate(); doc.Regenerate()
for vid, (org, hw, tags) in JOBS.items():
    v = doc.GetElement(ElementId(vid))
    kill = []
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'TAG LABEL': kill.append(e.Id)
        except Exception: pass
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    R = v.RightDirection
    OX, OY = org
    placed = []
    for (num, tgt, ztag) in tags:
        tx, ty, tz = tgt
        xel = (tx - OX) * R.X + (ty - OY) * R.Y
        sgn = 1.0 if xel >= 0 else -1.0
        xtag = sgn * (hw - 1.5)
        px = OX + R.X * xtag; py = OY + R.Y * xtag
        ex = OX + R.X * (xtag - sgn * 2.5); ey = OY + R.Y * (xtag - sgn * 2.5)
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(px, py, ztag), sym, v)
            p = fi.LookupParameter('TEXT')
            if p: p.Set(num)
            doc.Regenerate()
            e2 = doc.GetElement(fi.Id)
            try:
                e2.addLeader(); doc.Regenerate()
                lds = list(e2.GetLeaders())
                if lds:
                    lds[-1].End = _XYZ(tx, ty, tz)
                    try: lds[-1].Elbow = _XYZ(ex, ey, ztag)
                    except Exception: pass
            except Exception as ex3:
                L.append('  %s leader %s' % (num, str(ex3)[:40]))
            placed.append((fi.Id, num))
        except Exception as ex2:
            L.append('  %s FAIL %s' % (num, str(ex2)[:50]))
    doc.Regenerate()
    for eid, num in placed:
        p2 = doc.GetElement(eid).LookupParameter('TEXT')
        if p2 and p2.AsString() != num: p2.Set(num)
    L.append('%-16s %d tags' % (v.Name, len(placed)))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

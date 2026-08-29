# Keynote-tag the re-cut elevations/sections.  Tag sits at the paper edge on the
# same side as its target; leader elbow steps in, leader end lands on the element.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               ElementId, XYZ as _XYZ, BuiltInCategory as BIC)
from System.Collections.Generic import List
import math
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
CX, CY = 1161.1251, 98.8210
def W(s, t):
    return (CX + UX * s + VX * t, CY + UY * s + VY * t)
def S1(t): return W(-20.0, t)
def S2(t): return W(14.0, t)
def S3(s): return W(s, 11.0)
def S4(s): return W(s, -3.0)
# view id: (origin world, halfwidth, [(keynote, targetXYZ, tag z), ...])
JOBS = {
 2245103: ((1154.81, 123.60), 35.0, [   # North elevation
    ('2', (1135.5, 112.5, 14.7), 17.5), ('4', (1140.0, 113.5, 9.0), 10.0),
    ('5', (1148.2, 115.7, 7.2), 4.0),   ('6', (1152.6, 116.8, 3.5), 1.0),
    ('2', (1152.5, 116.8, 14.7), 19.5), ('1', (1180.4, 118.5, 24.5), 26.5),
    ('6', (1182.2, 119.7, 13.5), 13.0)]),
 2245112: ((1167.44, 74.04), 35.0, [    # South elevation
    ('7', (1185.8, 98.8, 4.0), 5.0),    ('8', (1168.0, 91.5, 9.0), 12.5),
    ('6', (1152.2, 92.4, 3.5), 1.0),    ('5', (1150.4, 89.8, 7.2), 8.0),
    ('2', (1149.5, 89.6, 17.2), 19.5),  ('2', (1131.8, 91.4, 3.2), 4.5),
    ('4', (1138.0, 90.5, 15.0), 15.5),  ('1', (1172.0, 95.0, 24.5), 26.5)]),
 2245121: ((1196.22, 107.77), 25.0, [   # East elevation
    ('1', (1186.0, 105.0, 24.5), 26.5), ('3', (1184.4, 99.1, 20.5), 21.5),
    ('6', (1182.6, 104.7, 13.5), 14.5), ('4', (1188.0, 110.0, 6.0), 6.0),
    ('8', (1180.0, 112.0, 16.0), 17.5)]),
 2245130: ((1126.03, 89.87), 25.0, [    # West elevation
    ('1', (1130.0, 100.0, 24.5), 26.5), ('2', (1131.9, 101.3, 14.7), 16.0),
    ('2', (1129.4, 100.8, 3.2), 4.5),   ('4', (1130.5, 95.0, 9.0), 9.5)]),
 2245139: ((1141.74, 93.88), 25.0, [    # Section 1
    ('1', S1(0.0) + (22.9,), 27.0),   ('11', S1(8.0) + (22.0,), 24.0),
    ('9', S1(-8.0) + (22.3,), 24.5),  ('7', S1(13.0) + (21.0,), 20.5),
    ('4', S1(13.0) + (16.0,), 16.5),  ('10', S1(-13.0) + (16.0,), 17.0),
    ('8', S1(-13.0) + (6.5,), 8.5),   ('2', S1(15.0) + (6.0,), 6.5),
    ('9', S1(0.0) + (11.5,), 12.0),   ('6', S1(14.0) + (1.2,), 2.0),
    ('5', S1(-14.0) + (1.5,), 3.5),   ('3', S1(0.0) + (0.5,), -1.0),
    ('12', S1(-15.0) + (-1.0,), -2.5)]),
 2245148: ((1174.69, 102.28), 25.0, [   # Section 2
    ('1', S2(0.0) + (22.9,), 27.0),   ('9', S2(6.0) + (22.3,), 24.0),
    ('4', S2(-8.0) + (16.0,), 17.0),  ('2', S2(13.0) + (6.0,), 6.5),
    ('8', S2(-12.0) + (6.5,), 9.0),   ('3', S2(0.0) + (0.5,), -1.0),
    ('12', S2(-12.0) + (-1.0,), -2.5)]),
 2245157: ((1158.41, 109.48), 35.0, [   # Section 3
    ('1', S3(0.0) + (22.9,), 27.0),   ('11', S3(-12.0) + (22.0,), 24.5),
    ('9', S3(10.0) + (22.3,), 24.0),  ('7', S3(-22.0) + (21.0,), 20.5),
    ('4', S3(18.0) + (16.0,), 16.5),  ('10', S3(-25.0) + (15.5,), 17.0),
    ('2', S3(-28.0) + (6.0,), 6.5),   ('8', S3(22.0) + (6.5,), 9.0),
    ('6', S3(-27.0) + (1.2,), 2.0),   ('5', S3(26.0) + (1.5,), 3.5),
    ('3', S3(0.0) + (0.5,), -1.0),    ('12', S3(-20.0) + (-1.0,), -2.5)]),
 2245166: ((1161.87, 95.91), 35.0, [    # Section 4
    ('1', S4(0.0) + (22.9,), 27.0),   ('9', S4(-10.0) + (22.3,), 24.0),
    ('4', S4(12.0) + (16.0,), 16.5),  ('2', S4(-28.0) + (6.0,), 6.5),
    ('8', S4(20.0) + (6.5,), 9.0),    ('3', S4(0.0) + (0.5,), -1.0),
    ('12', S4(18.0) + (-1.0,), -2.5)]),
}
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
L = []
t = Transaction(doc, 'OneTake: retag re-cut views'); _prep(t); t.Start()
if not sym.IsActive: sym.Activate(); doc.Regenerate()
for vid, (org, hw, tags) in JOBS.items():
    v = doc.GetElement(ElementId(vid))
    # wipe any existing TAG LABELs in this view
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
        xtag = sgn * (hw - 2.0)
        px = OX + R.X * xtag; py = OY + R.Y * xtag
        ex = OX + R.X * (xtag - sgn * 3.0); ey = OY + R.Y * (xtag - sgn * 3.0)
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
            L.append('  %s place FAIL %s' % (num, str(ex2)[:50]))
    doc.Regenerate()
    bad = 0
    for eid, num in placed:
        p2 = doc.GetElement(eid).LookupParameter('TEXT')
        if p2 and p2.AsString() != num:
            p2.Set(num)
            if doc.GetElement(eid).LookupParameter('TEXT').AsString() != num: bad += 1
    L.append('%-16s %d tags placed%s' % (v.Name, len(placed),
                                         (', %d BAD' % bad) if bad else ', verified'))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

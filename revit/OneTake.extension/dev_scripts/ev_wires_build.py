# Match Francis's convention:
#   - real Revit Wire elements (arc) from each door switch to the fixture it runs,
#     replacing the detail-line arcs I had drawn
#   - flip every outlet/switch that ended up on the OUTSIDE face of its wall
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
from Autodesk.Revit.DB.Electrical import Wire, WireType, WiringType
from System.Collections.Generic import List
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
V1, V2 = 2244950, 2244908
CENX, CENY = 1157.520, 104.867
# switch -> fixture pairs (the Bed-2 one is Francis's, leave it alone)
W1 = [((1140.9, 106.0), (1135.3, 106.7)), ((1141.5, 102.9), (1144.6, 106.3)),
      ((1145.9, 99.9), (1146.7, 94.6)),   ((1153.9, 92.8), (1152.6, 98.3)),
      ((1154.9, 117.4), (1158.8, 112.2)), ((1176.9, 96.6), (1176.6, 114.5)),
      ((1184.9, 98.6), (1181.5, 116.8)),  ((1141.8, 105.6), (1141.8, 108.9))]
W2 = [((1142.4, 100.1), (1140.6, 92.9)),  ((1145.0, 102.8), (1148.6, 106.5)),
      ((1146.9, 103.3), (1155.7, 106.7)), ((1147.4, 99.4), (1147.7, 94.7)),
      ((1172.4, 95.5), (1163.7, 98.7)),   ((1178.0, 109.1), (1173.2, 110.0)),
      ((1141.6, 109.2), (1138.1, 107.4))]
wt = None
for x in FEC(pdoc).OfClass(WireType):
    wt = x; break
L = ['wire type: %s' % (wt.Id.Value if wt else 'NONE')]
t = Transaction(pdoc, 'OneTake: real wires + flip devices'); _prep(t); t.Start()
# --- drop my detail-line switch legs from the two ELEC views (mech duct runs stay) ---
kill = []
for vid in (V1, V2):
    v = pdoc.GetElement(ElementId(vid))
    for e in FEC(pdoc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType():
        if e.OwnerViewId == v.Id: kill.append(e.Id)
if kill:
    pdoc.Delete(List[ElementId](kill))
    L.append('removed %d detail-line switch legs' % len(kill))
pdoc.Regenerate()
# --- remove my duplicate Bed-2 switch if Francis's is there ---
his = pdoc.GetElement(ElementId(2245614))
mine = pdoc.GetElement(ElementId(2244854))
if his is not None and mine is not None:
    pdoc.Delete(ElementId(2244854))
    L.append('deleted my duplicate Bed-2 switch 2244854')
pdoc.Regenerate()
# --- real wires ---
for vid, pairs in ((V1, W1), (V2, W2)):
    n = 0
    for (a, b) in pairs:
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1.0
        px, py = -dy / d, dx / d
        bulge = min(4.0, max(1.5, d * 0.45))
        mx, my = (ax + bx) / 2.0 + px * bulge, (ay + by) / 2.0 + py * bulge
        pts = List[_XYZ]()
        pts.Add(_XYZ(ax, ay, 0)); pts.Add(_XYZ(mx, my, 0)); pts.Add(_XYZ(bx, by, 0))
        try:
            Wire.Create(pdoc, wt.Id, ElementId(vid), WiringType.Arc, pts, None, None)
            n += 1
        except Exception as ex:
            L.append('  wire fail %s' % str(ex)[:60])
    L.append('view %s: %d wires created' % (vid, n))
pdoc.Regenerate()
# --- flip devices that sit on the outside face of the wall ---
flipped = failed = 0
for e in FEC(pdoc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        p = e.Location.Point
        f = e.FacingOrientation
    except Exception:
        continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    dxx, dyy = CENX - p.X, CENY - p.Y
    m = math.hypot(dxx, dyy) or 1.0
    if (f.X * dxx + f.Y * dyy) / m >= 0: continue      # already faces inward
    try:
        if e.CanFlipFacing:
            e.flipFacing(); flipped += 1
        else:
            failed += 1
    except Exception:
        failed += 1
L.append('flipped %d devices inward (%d could not flip)' % (flipped, failed))
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)

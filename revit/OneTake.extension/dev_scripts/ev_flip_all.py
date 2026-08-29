# Flip every outlet / switch whose symbol draws on the OUTSIDE face of its wall,
# so it reads inside the room. Facing is compared against the wall's inward side
# (from the host wall, not the building centre - interior walls need that).
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC)
CENX, CENY = 1157.520, 104.867
def inward_ok(e):
    """True when the device already faces the room side of its host wall."""
    p = e.Location.Point
    f = e.FacingOrientation
    h = None
    try: h = e.Host
    except Exception: pass
    ref = None
    if h is not None:
        try:
            c = h.Location.Curve
            a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
            dx, dy = b0.X - a0.X, b0.Y - a0.Y
            m = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / m, dx / m
            # pick the wall normal that points toward the building interior
            if nx * (CENX - p.X) + ny * (CENY - p.Y) < 0: nx, ny = -nx, -ny
            ref = (nx, ny)
        except Exception: ref = None
    if ref is None:
        dxx, dyy = CENX - p.X, CENY - p.Y
        m = math.hypot(dxx, dyy) or 1.0
        ref = (dxx / m, dyy / m)
    return (f.X * ref[0] + f.Y * ref[1]) >= 0
targets = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if not inward_ok(e): targets.append(e)
L = ['%d devices face outward' % len(targets)]
t = Transaction(doc, 'OneTake: flip outlets inward'); _prep(t); t.Start()
ok = bad = 0
for e in targets:
    before = e.FacingFlipped
    try:
        e.flipFacing()
        doc.Regenerate()
        if e.FacingFlipped != before: ok += 1
        else: bad += 1
    except Exception as ex:
        bad += 1
        L.append('  %s FAIL %s' % (e.Id.Value, str(ex)[:50]))
doc.Regenerate(); t.Commit()
L.append('flipped %d, unchanged %d' % (ok, bad))
still = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if not inward_ok(e): still += 1
L.append('still facing outward: %d' % still)
result = '\n'.join(L)

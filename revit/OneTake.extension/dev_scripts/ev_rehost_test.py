# Re-place one kitchen GFI with its insertion point on the ROOM side of the wall -
# for wall-hosted families Revit picks the side from the insertion point.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
CENX, CENY = 1157.520, 104.867
L = []
e = pdoc.GetElement(ElementId(2244839))
p = e.Location.Point
sym = e.Symbol
host = e.Host
lvl = pdoc.GetElement(e.LevelId) if e.LevelId != ElementId.InvalidElementId else None
if lvl is None:
    for lv in FEC(pdoc).OfClass(__import__('Autodesk').Revit.DB.Level):
        if abs(lv.Elevation - 0.67) < 0.01: lvl = lv; break
elev = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
zoff = elev.AsDouble() if elev else 3.0
# inward direction from the wall
c = host.Location.Curve
a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
dx, dy = b0.X - a0.X, b0.Y - a0.Y
m = math.hypot(dx, dy)
n1 = (-dy / m, dx / m)
to_c = (CENX - p.X, CENY - p.Y)
if n1[0] * to_c[0] + n1[1] * to_c[1] < 0: n1 = (-n1[0], -n1[1])   # point it inward
L.append('inward normal (%.3f,%.3f); old loc (%.3f,%.3f) flipped=%s' % (
    n1[0], n1[1], p.X, p.Y, e.FacingFlipped))
t = Transaction(pdoc, 'OneTake: rehost test'); _prep(t); t.Start()
pdoc.Delete(e.Id)
pdoc.Regenerate()
np = _XYZ(p.X + n1[0] * 0.35, p.Y + n1[1] * 0.35, p.Z)
try:
    fi = pdoc.Create.NewFamilyInstance(np, sym, host, lvl, StructuralType.NonStructural)
    pdoc.Regenerate()
    L.append('new %s loc (%.3f,%.3f) facing (%.2f,%.2f) flipped=%s' % (
        fi.Id.Value, fi.Location.Point.X, fi.Location.Point.Y,
        fi.FacingOrientation.X, fi.FacingOrientation.Y, fi.FacingFlipped))
    pe = fi.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
    if pe and not pe.IsReadOnly: pe.Set(zoff)
    try: fi.get_Parameter(BIP.PHASE_CREATED).Set(host.CreatedPhaseId)
    except Exception: pass
except Exception as ex:
    L.append('create FAILED %s' % str(ex)[:70])
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)

# Can a 180-degree rotation (or a mirror) turn the outlet symbol into the room?
import math
from Autodesk.Revit.DB import (ElementId, XYZ as _XYZ, Line, ElementTransformUtils,
                               Plane)
from System.Collections.Generic import List
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = []
e = pdoc.GetElement(ElementId(2244839))
p = e.Location.Point
L.append('before facing (%.2f,%.2f)' % (e.FacingOrientation.X, e.FacingOrientation.Y))
t = Transaction(pdoc, 'OneTake: rotate test'); _prep(t); t.Start()
try:
    ax = Line.CreateBound(_XYZ(p.X, p.Y, p.Z), _XYZ(p.X, p.Y, p.Z + 1))
    ElementTransformUtils.RotateElement(pdoc, e.Id, ax, math.pi)
    pdoc.Regenerate()
    e2 = pdoc.GetElement(ElementId(2244839))
    L.append('after rotate facing (%.2f,%.2f)  loc (%.3f,%.3f)' % (
        e2.FacingOrientation.X, e2.FacingOrientation.Y,
        e2.Location.Point.X, e2.Location.Point.Y))
except Exception as ex:
    L.append('rotate FAILED: %s' % str(ex)[:80])
t.RollBack()
# mirror across the wall plane as a fallback
t2 = Transaction(pdoc, 'OneTake: mirror test'); _prep(t2); t2.Start()
try:
    h = e.Host
    c = h.Location.Curve
    a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
    dx, dy = b0.X - a0.X, b0.Y - a0.Y
    m = math.hypot(dx, dy)
    nrm = _XYZ(-dy / m, dx / m, 0)
    pl = Plane.CreateByNormalAndOrigin(nrm, _XYZ(p.X, p.Y, p.Z))
    ids = List[ElementId](); ids.Add(e.Id)
    ElementTransformUtils.MirrorElements(pdoc, ids, pl, False)
    pdoc.Regenerate()
    e3 = pdoc.GetElement(ElementId(2244839))
    L.append('after mirror facing (%.2f,%.2f)' % (
        e3.FacingOrientation.X, e3.FacingOrientation.Y))
except Exception as ex:
    L.append('mirror FAILED: %s' % str(ex)[:80])
t2.RollBack()
result = '\n'.join(L)

# Last API route: LocationPoint.Rotate (a different code path to ElementTransformUtils).
import math
from Autodesk.Revit.DB import ElementId, XYZ as _XYZ, Line
e = doc.GetElement(ElementId(2245692))
p = e.Location.Point
L = ['before facing (%.2f,%.2f) flipped=%s' % (
    e.FacingOrientation.X, e.FacingOrientation.Y, e.FacingFlipped)]
t = Transaction(doc, 'OneTake: locrot test'); _prep(t); t.Start()
try:
    ax = Line.CreateBound(_XYZ(p.X, p.Y, p.Z), _XYZ(p.X, p.Y, p.Z + 1))
    ok = e.Location.Rotate(ax, math.pi)
    doc.Regenerate()
    e2 = doc.GetElement(ElementId(2245692))
    L.append('Location.Rotate returned %s -> facing (%.2f,%.2f) flipped=%s' % (
        ok, e2.FacingOrientation.X, e2.FacingOrientation.Y, e2.FacingFlipped))
except Exception as ex:
    L.append('Location.Rotate FAILED %s' % str(ex)[:70])
t.RollBack()
result = '\n'.join(L)

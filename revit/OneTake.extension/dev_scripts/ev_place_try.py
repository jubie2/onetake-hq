# Try the placement overloads that can control which side a hosted device sits on.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               HostObjectUtils, ShellLayerType, Level,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
CENX, CENY = 1157.520, 104.867
L = []
e = doc.GetElement(ElementId(2245692))
p = e.Location.Point; sym = e.Symbol; h = e.Host
lvl = doc.GetElement(e.LevelId)
zoff = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM).AsDouble()
c = h.Location.Curve
a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
dx, dy = b0.X - a0.X, b0.Y - a0.Y
m = math.hypot(dx, dy)
nx, ny = -dy / m, dx / m
if nx * (CENX - p.X) + ny * (CENY - p.Y) < 0: nx, ny = -nx, -ny   # inward
L.append('inward (%.3f,%.3f), current facing (%.2f,%.2f)' % (
    nx, ny, e.FacingOrientation.X, e.FacingOrientation.Y))
# --- attempt A: referenceDirection overload ---
t = Transaction(doc, 'OneTake: place try A'); _prep(t); t.Start()
try:
    doc.Delete(e.Id); doc.Regenerate()
    fi = doc.Create.NewFamilyInstance(_XYZ(p.X, p.Y, p.Z), sym, _XYZ(nx, ny, 0), h,
                                      StructuralType.NonStructural)
    doc.Regenerate()
    L.append('A refDir overload -> facing (%.2f,%.2f) flipped=%s' % (
        fi.FacingOrientation.X, fi.FacingOrientation.Y, fi.FacingFlipped))
except Exception as ex:
    L.append('A FAILED %s' % str(ex)[:70])
t.RollBack()
# --- attempt B: host on the wall's interior FACE ---
t2 = Transaction(doc, 'OneTake: place try B'); _prep(t2); t2.Start()
try:
    doc.Delete(ElementId(2245692)); doc.Regenerate()
    refs = HostObjectUtils.GetSideFaces(h, ShellLayerType.Interior)
    fi2 = doc.Create.NewFamilyInstance(refs[0], _XYZ(p.X, p.Y, p.Z), _XYZ(nx, ny, 0), sym)
    doc.Regenerate()
    L.append('B interior-face -> facing (%.2f,%.2f) flipped=%s' % (
        fi2.FacingOrientation.X, fi2.FacingOrientation.Y, fi2.FacingFlipped))
except Exception as ex:
    L.append('B FAILED %s' % str(ex)[:70])
t2.RollBack()
result = '\n'.join(L)

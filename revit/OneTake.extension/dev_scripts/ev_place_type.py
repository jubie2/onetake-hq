# What placement type are these families, and can we host on the wall's INTERIOR face?
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               HostObjectUtils, ShellLayerType, Options,
                               BuiltInCategory as BIC, Plane, ElementTransformUtils)
from System.Collections.Generic import List
L = []
e = None
for x in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    if x.Id.Value == 2245692: e = x; break
if e is None:
    for x in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
        try: p = x.Location.Point
        except Exception: continue
        if p and 1155 < p.X < 1158 and 116 < p.Y < 119: e = x; break
L.append('sample %s %s' % (e.Id.Value, e.Symbol.Family.Name))
fam = e.Symbol.Family
L.append('  placement type: %s' % fam.FamilyPlacementType)
L.append('  work plane based: %s' % fam.get_Parameter(
    __import__('Autodesk').Revit.DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
    if False else 'n/a')
h = e.Host
L.append('  host %s  %s' % (h.Id.Value, h.Name[:30]))
for side, nm in ((ShellLayerType.Interior, 'Interior'), (ShellLayerType.Exterior, 'Exterior')):
    try:
        refs = HostObjectUtils.GetSideFaces(h, side)
        L.append('  %s side faces: %d' % (nm, refs.Count))
    except Exception as ex:
        L.append('  %s side faces FAILED %s' % (nm, str(ex)[:40]))
# try a real mirror, committed, and see whether facing changes
p = e.Location.Point
L.append('  before facing (%.2f,%.2f) flipped=%s' % (
    e.FacingOrientation.X, e.FacingOrientation.Y, e.FacingFlipped))
c = h.Location.Curve
a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
dx, dy = b0.X - a0.X, b0.Y - a0.Y
m = math.hypot(dx, dy)
t = Transaction(doc, 'OneTake: mirror commit test'); _prep(t); t.Start()
try:
    pl = Plane.CreateByNormalAndOrigin(_XYZ(-dy / m, dx / m, 0), _XYZ(p.X, p.Y, p.Z))
    ids = List[ElementId](); ids.Add(e.Id)
    ElementTransformUtils.MirrorElements(doc, ids, pl, False)
    doc.Regenerate()
    e2 = doc.GetElement(e.Id)
    if e2 is None:
        L.append('  mirror: original consumed')
    else:
        L.append('  after mirror facing (%.2f,%.2f) flipped=%s' % (
            e2.FacingOrientation.X, e2.FacingOrientation.Y, e2.FacingFlipped))
except Exception as ex:
    L.append('  mirror FAILED %s' % str(ex)[:70])
t.RollBack()
result = '\n'.join(L)

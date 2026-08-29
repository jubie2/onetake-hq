# Does the rebuilt wall exist, and is it visible in the 1st-floor plan views?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Wall,
                               BuiltInParameter as BIP)
w = doc.GetElement(ElementId(2245709))
L = []
if w is None:
    L.append('wall 2245709 MISSING')
else:
    bb = w.get_BoundingBox(None)
    c = w.Location.Curve
    L.append('wall 2245709 "%s"' % w.Name)
    L.append('  curve (%.2f,%.2f)->(%.2f,%.2f)  z %.2f..%.2f' % (
        c.GetEndPoint(0).X, c.GetEndPoint(0).Y, c.GetEndPoint(1).X, c.GetEndPoint(1).Y,
        bb.Min.Z, bb.Max.Z))
    for bip, nm in ((BIP.WALL_BASE_CONSTRAINT, 'base'), (BIP.WALL_USER_HEIGHT_PARAM, 'height'),
                    (BIP.PHASE_CREATED, 'phase'), (BIP.PHASE_DEMOLISHED, 'demolished')):
        p = w.get_Parameter(bip)
        L.append('  %-11s %s' % (nm, p.AsValueString() if p else '-'))
    sib = doc.GetElement(ElementId(2189094))
    L.append('sibling phase %s / demolished %s' % (
        sib.get_Parameter(BIP.PHASE_CREATED).AsValueString(),
        sib.get_Parameter(BIP.PHASE_DEMOLISHED).AsValueString()))
for vid, nm in ((718579, '1st Floor Plan'), (2244950, 'ADU 1st Floor Elec'),
                (2244930, 'ADU 1st Floor Mech')):
    v = doc.GetElement(ElementId(vid))
    if v is None: L.append('view %s missing' % vid); continue
    found = any(x.Id.Value == 2245709 for x in FEC(doc, v.Id).OfClass(Wall))
    L.append('  visible in %-22s : %s' % (nm, found))
result = '\n'.join(L)

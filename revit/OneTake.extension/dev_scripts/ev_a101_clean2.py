# A101: delete stale BLDG3&4 note, move north arrows to the new title lines.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
t = Transaction(doc, 'OneTake: A101 cleanup'); _prep(t); t.Start()
doc.Delete(ElementId(2147083))
moves = {2056108: (1.04, 0.92), 2056120: (2.12, 0.92)}
L = ['deleted stale BLDG3&4 note']
for eid, (x, y) in moves.items():
    e = doc.GetElement(ElementId(eid))
    bb = e.get_BoundingBox(doc.GetElement(e.OwnerViewId))
    cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
    e.Location.Move(_XYZ(x - cx, y - cy, 0))
    L.append('arrow %d -> (%.2f,%.2f)' % (eid, x, y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

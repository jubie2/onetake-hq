# A01: move building-analysis text down; delete the old strike-out X lines.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               CurveElement, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s
kill = []
for e in FEC(doc, sh.Id).OfClass(CurveElement):
    bb = e.get_BoundingBox(sh)
    if bb and 1.3 < bb.Min.X < 1.8 and 0.3 < bb.Min.Y < 0.8 and \
       (bb.Max.X - bb.Min.X) > 0.1 and (bb.Max.Y - bb.Min.Y) > 0.1:
        kill.append(e.Id)
t = Transaction(doc, 'OneTake: A01 polish'); _prep(t); t.Start()
if kill:
    doc.Delete(List[ElementId](kill))
    L.append('deleted %d strike lines' % len(kill))
e = doc.GetElement(ElementId(1132943))
c = e.Coord
e.Coord = _XYZ(c.X, c.Y - 0.05, 0)
L.append('analysis text moved to (%.2f,%.2f)' % (c.X, c.Y - 0.05))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

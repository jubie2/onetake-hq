# Put wall 2189148 back the way it was, and confirm the device count is intact.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
w = doc.GetElement(ElementId(2189148))
L = ['orientation before restore (%.3f,%.3f)' % (w.Orientation.X, w.Orientation.Y)]
t = Transaction(doc, 'OneTake: restore wall'); _prep(t); t.Start()
if abs(w.Orientation.X - 0.247) < 0.01:          # currently flipped from original
    w.Flip(); doc.Regenerate()
L.append('orientation after  (%.3f,%.3f)' % (w.Orientation.X, w.Orientation.Y))
t.Commit()
n1 = n2 = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if p.Z < 10: n1 += 1
    else: n2 += 1
L.append('devices: %d on 1st floor, %d on 2nd (was 26 / 21)' % (n1, n2))
result = '\n'.join(L)

# Decisive test: flip the north kitchen wall for real and report orientation +
# device facing (the render will show whether the symbols moved inside).
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ElementId, BuiltInCategory as BIC
w = doc.GetElement(ElementId(2189148))
devs = []
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        if e.Host and e.Host.Id.Value == 2189148: devs.append(e)
    except Exception: pass
L = ['wall orientation before (%.3f,%.3f)' % (w.Orientation.X, w.Orientation.Y)]
for e in devs[:3]:
    L.append('  dev %s facing (%.2f,%.2f)' % (
        e.Id.Value, e.FacingOrientation.X, e.FacingOrientation.Y))
t = Transaction(doc, 'OneTake: flip kitchen wall'); _prep(t); t.Start()
try:
    w.Flip()
    doc.Regenerate()
    L.append('wall orientation after  (%.3f,%.3f)' % (w.Orientation.X, w.Orientation.Y))
    for e in devs[:3]:
        e2 = doc.GetElement(e.Id)
        L.append('  dev %s facing (%.2f,%.2f)' % (
            e2.Id.Value, e2.FacingOrientation.X, e2.FacingOrientation.Y))
except Exception as ex:
    L.append('flip FAILED %s' % str(ex)[:70])
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

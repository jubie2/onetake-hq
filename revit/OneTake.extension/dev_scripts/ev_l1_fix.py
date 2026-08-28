# L1: remove the stale old-site 'Landscaping Plan Copy 1' viewport.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, Viewport
L = []
t = Transaction(doc, 'OneTake: L1 fix'); _prep(t); t.Start()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'L1': continue
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        if v.Name == 'Landscaping Plan Copy 1':
            doc.Delete(vp.Id)
            L.append('removed stale viewport')
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'not found'

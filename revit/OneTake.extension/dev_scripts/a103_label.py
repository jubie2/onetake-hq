# Nudge the ROOF LEGEND viewport label down so it clears the attic note on A103.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               XYZ as _XYZ)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A103': sh = s; break
t = Transaction(doc, 'OneTake: A103 label'); _prep(t); t.Start()
L = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name == 'ROOF LEGEND':
        try:
            o = vp.LabelOffset
            vp.LabelOffset = _XYZ(o.X, o.Y - 0.06, 0)
            L.append('label moved from (%.3f,%.3f)' % (o.X, o.Y))
        except Exception as ex:
            L.append('FAIL %s' % str(ex)[:60])
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'not found'

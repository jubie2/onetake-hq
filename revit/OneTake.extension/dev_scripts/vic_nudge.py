# Compensate the raster draw offset (paper margin) by moving the instance (-0.085,-0.085).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ImageInstance,
                               ElementTransformUtils, XYZ as _XYZ)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
L = []
t = Transaction(doc, 'OneTake: vicinity nudge'); _prep(t); t.Start()
for e in FEC(doc, sh.Id).OfClass(ImageInstance):
    tn = doc.GetElement(e.GetTypeId())
    nm = ''
    try: nm = e.Name or ''
    except Exception: pass
    b0 = e.get_BoundingBox(sh)
    ElementTransformUtils.MoveElement(doc, e.Id, _XYZ(-0.085, -0.085, 0))
    b1 = e.get_BoundingBox(sh)
    L.append('%s %s: (%.3f,%.3f) -> (%.3f,%.3f)' % (e.Id, nm[:22], b0.Min.X, b0.Min.Y, b1.Min.X, b1.Min.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

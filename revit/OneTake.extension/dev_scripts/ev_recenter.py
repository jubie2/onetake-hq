# Re-center A200/A201 1st-floor viewports after crop rotation.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: recenter'); _prep(t); t.Start()
for sn, vid, cx, cy in [('A200', 2244930, 2.36, 1.42), ('A201', 2244950, 1.76, 1.30)]:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn:
            for vp in FEC(doc, s.Id).OfClass(Viewport):
                if vp.ViewId.Value == vid:
                    vp.SetBoxCenter(_XYZ(cx, cy, 0))
                    doc.Regenerate()
                    ol = vp.GetBoxOutline()
                    L.append('%s (%.2f,%.2f)-(%.2f,%.2f)' % (sn,
                             ol.MinimumPoint.X, ol.MinimumPoint.Y,
                             ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

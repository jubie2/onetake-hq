# A02: bring the Site viewport onto the sheet above its title.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: A02 site vp'); _prep(t); t.Start()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A02': continue
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        if v.Name == 'Site':
            vp.SetBoxCenter(_XYZ(0.85, 1.33, 0))
            doc.Regenerate()
            ol = vp.GetBoxOutline()
            try: vp.LabelOffset = _XYZ(0.06, -0.045, 0)
            except Exception: pass
            L.append('Site vp -> box (%.2f,%.2f)-(%.2f,%.2f) scale 1:%d' % (
                ol.MinimumPoint.X, ol.MinimumPoint.Y,
                ol.MaximumPoint.X, ol.MaximumPoint.Y, v.Scale))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

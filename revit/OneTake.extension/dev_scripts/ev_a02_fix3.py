# Restore Site view original crop, center on sheet, tuck title next to north arrow.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               XYZ as _XYZ, BoundingBoxXYZ)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A02': sh = s
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    vv = doc.GetElement(vp.ViewId)
    if vv.Name == 'Site': v = vv; svp = vp
t = Transaction(doc, 'OneTake: A02 crop restore'); _prep(t); t.Start()
cb = v.CropBox
nb = BoundingBoxXYZ(); nb.Transform = cb.Transform
nb.Min = _XYZ(1132.7, -555.2, cb.Min.Z)
nb.Max = _XYZ(1289.2, -417.2, cb.Max.Z)
v.CropBox = nb
doc.Regenerate()
svp.SetBoxCenter(_XYZ(0.85, 1.33, 0))
doc.Regenerate()
try: svp.LabelOffset = _XYZ(0.58, 0.05, 0)
except Exception: pass
doc.Regenerate(); t.Commit()
ol = svp.GetBoxOutline()
result = 'Site box (%.2f,%.2f)-(%.2f,%.2f)' % (
    ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y)

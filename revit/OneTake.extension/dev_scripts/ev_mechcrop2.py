# Re-apply crop to the new 1st-floor mech view and re-center its viewport.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, BoundingBoxXYZ)
src = doc.GetElement(ElementId(718579))
mv = doc.GetElement(ElementId(2244930))
t = Transaction(doc, 'OneTake: mech crop2'); _prep(t); t.Start()
cb = src.CropBox
nb = BoundingBoxXYZ(); nb.Transform = cb.Transform
nb.Min = cb.Min; nb.Max = cb.Max
mv.CropBox = nb
mv.CropBoxActive = True
doc.Regenerate()
L = ['crop set active=%s' % mv.CropBoxActive]
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200':
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if vp.ViewId.Value == 2244930:
                vp.SetBoxCenter(_XYZ(2.36, 1.42, 0))
                doc.Regenerate()
                ol = vp.GetBoxOutline()
                L.append('vp (%.2f,%.2f)-(%.2f,%.2f)' % (
                    ol.MinimumPoint.X, ol.MinimumPoint.Y,
                    ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

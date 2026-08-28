# BMP view: 1"=13'-4" too big; set 1:160 and re-center.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ)
v = doc.GetElement(ElementId(2244991))
t = Transaction(doc, 'OneTake: BMP scale'); _prep(t); t.Start()
v.Scale = 160
doc.Regenerate()
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A06':
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if vp.ViewId.Value == 2244991:
                vp.SetBoxCenter(_XYZ(1.45, 1.48, 0))
                doc.Regenerate()
                ol = vp.GetBoxOutline()
                L.append('vp (%.2f,%.2f)-(%.2f,%.2f)' % (
                    ol.MinimumPoint.X, ol.MinimumPoint.Y,
                    ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

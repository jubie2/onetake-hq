# Broad: all Lines-category elements on A01.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, CurveElement
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s
for e in FEC(doc, sh.Id).OfClass(CurveElement):
    bb = e.get_BoundingBox(sh)
    if bb:
        L.append('%s (%.2f,%.2f)-(%.2f,%.2f) style=%s' % (e.Id.Value,
                 bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y,
                 e.LineStyle.Name if e.LineStyle else '?'))
result = '\n'.join(L) or 'no curve elements on sheet'

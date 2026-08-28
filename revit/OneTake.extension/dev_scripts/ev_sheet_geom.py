# Measure A101 sheet outline, titleblock, and each viewport's box + label offset.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               BuiltInCategory as BIC)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A101': continue
    o = s.Outline
    L.append('sheet outline (%.2f,%.2f)-(%.2f,%.2f)' % (o.Min.U, o.Min.V, o.Max.U, o.Max.V))
    for tb in FEC(doc, s.Id).OfCategory(BIC.OST_TitleBlocks):
        bb = tb.get_BoundingBox(s)
        L.append('titleblock bbox (%.2f,%.2f)-(%.2f,%.2f)' % (
            bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y))
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        ol = vp.GetBoxOutline()
        try: lo = vp.LabelOffset; lof = '(%.2f,%.2f)' % (lo.X, lo.Y)
        except Exception: lof = '?'
        L.append('%s: box (%.2f,%.2f)-(%.2f,%.2f) size %.2fx%.2f label %s scale 1:%d' % (
            v.Name, ol.MinimumPoint.X, ol.MinimumPoint.Y,
            ol.MaximumPoint.X, ol.MaximumPoint.Y,
            ol.MaximumPoint.X - ol.MinimumPoint.X,
            ol.MaximumPoint.Y - ol.MinimumPoint.Y, lof,
            v.Scale if hasattr(v, 'Scale') else 0))
result = '\n'.join(L)

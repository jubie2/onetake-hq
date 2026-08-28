# List A01 text notes (ids + coords + text) and viewports.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, TextNote,
                               Viewport)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A01': continue
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        c = vp.GetBoxCenter()
        L.append('VP [%s] %s (view %s) at (%.2f,%.2f)' % (
            v.ViewType, v.Name, v.Id.Value, c.X, c.Y))
    for e in FEC(doc, s.Id).OfClass(TextNote):
        txt = (e.Text or '').replace('\r', '|').replace('\n', '|')
        c = e.Coord
        L.append('TEXT %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y, txt[:110]))
result = '\n'.join(L)

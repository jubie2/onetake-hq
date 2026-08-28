# Inspect ELEVATION KEYNOTES legend: texts + annotation symbols.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               FamilyInstance)
lv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ELEVATION KEYNOTES': lv = v; break
L = ['legend id %s' % lv.Id.Value]
for e in FEC(doc, lv.Id).OfClass(TextNote):
    c = e.Coord
    L.append('TEXT %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
             (e.Text or '').replace('\n', '|')[:60]))
for e in FEC(doc, lv.Id).OfClass(FamilyInstance):
    bb = e.get_BoundingBox(lv)
    if bb:
        L.append('FAM %s "%s" (%.2f,%.2f)' % (e.Id.Value, e.Symbol.Family.Name,
                 (bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2))
result = '\n'.join(L)

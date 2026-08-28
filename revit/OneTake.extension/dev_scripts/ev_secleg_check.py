from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
lv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'KEYNOTES SECTION': lv = v; break
L = []
for e in FEC(doc, lv.Id).OfClass(TextNote):
    c = e.Coord
    L.append('%s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
             (e.Text or '').replace('\r', '|').replace('\n', '|')[:50]))
result = '\n'.join(sorted(L))

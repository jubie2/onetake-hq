# Full text of TextNotes in a view. args {"view":"KEYNOTES SECTION"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
nm = args.get('view')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = []
for e in FEC(doc, v.Id).OfClass(TextNote):
    p = e.Coord
    L.append('=== (%.2f,%.2f) id %s ===\n%s' % (p.X, p.Y, e.Id.Value,
             (e.Text or '').replace('\r', '\n')))
result = '\n'.join(L)

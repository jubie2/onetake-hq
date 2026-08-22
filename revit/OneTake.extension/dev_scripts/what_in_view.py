# List categories + element counts visible in a view. args {"view":"ADU - Section 2"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
counts = {}
for e in FEC(doc, v.Id):
    try:
        c = e.Category
        k = c.Name if c else '(none)'
    except Exception:
        k = '(err)'
    counts[k] = counts.get(k, 0) + 1
L = ['%s: %d categories' % (nm, len(counts))]
for k in sorted(counts, key=lambda z: -counts[z]):
    L.append('  %-32s %d' % (k, counts[k]))
result = '\n'.join(L)

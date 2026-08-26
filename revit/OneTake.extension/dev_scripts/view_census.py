# Count every element by category/class in a view, list annotation-ish ones fully.
# args {"view":"ADU - West Elevation"}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View
nm = args.get('view')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
cnt = {}
detail = []
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    cn = e.Category.Name if e.Category else '(none)'
    k = '%s / %s' % (cn, e.GetType().Name)
    cnt[k] = cnt.get(k, 0) + 1
    if cn in ('Lines', 'Detail Items', 'Generic Annotations', 'Text Notes',
              'Multi-Category Tags', 'Arrows', 'Leader', 'Symbols'):
        try:
            fam = e.Symbol.Family.Name + ':' + str(e.Id.Value)
        except Exception:
            fam = str(e.Id.Value)
        detail.append('%s %s' % (k, fam))
L = ['view %s' % nm]
for k in sorted(cnt):
    L.append('%3d  %s' % (cnt[k], k))
L.append('--- detail ---')
L.extend(detail[:60])
result = '\n'.join(L)

# List Window/Door types with their width/height so we can match traced openings.
from Autodesk.Revit.DB import FamilySymbol, BuiltInParameter, BuiltInCategory, StorageType
rows = []
for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
    cat = fs.Category.Name if fs.Category else ''
    only = args.get('cat', 'Windows')
    if cat != only:
        continue
    def p(n):
        q = fs.LookupParameter(n)
        if q is None or q.StorageType != StorageType.Double: return None
        return round(q.AsDouble(), 3)
    w = p('Width') or p('Rough Width')
    h = p('Height') or p('Rough Height')
    nm = fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    rows.append((cat, fs.FamilyName, nm, w, h, fs.Id.Value))
rows.sort(key=lambda r: (r[0], -(r[3] or 0)))
L = ['%-8s %-34s %-22s %6s %6s  %s' % ('CAT', 'FAMILY', 'TYPE', 'W', 'H', 'ID')]
for c, f, n, w, h, i in rows[:70]:
    L.append('%-8s %-34s %-22s %6s %6s  %s' % (c, f[:34], (n or '')[:22],
             ('%.2f' % w) if w else '-', ('%.2f' % h) if h else '-', i))
L.append('total window/door types: %d' % len(rows))
result = '\n'.join(L)

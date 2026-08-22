# Find rooms by name substrings and report level + location. args {"names":["Bed","Bath","Family","Garage","Kitchen"]}
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, View
want = [n.lower() for n in args.get('names', [])]
L = []
hits = []
for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms):
    try:
        nm = r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() or ''
        if not any(w in nm.lower() for w in want):
            continue
        if r.Area <= 0:
            continue
        p = r.Location.Point
        lv = doc.GetElement(r.LevelId)
        hits.append((nm, r.Id.Value, lv.Name if lv else '?', round(p.X,1), round(p.Y,1), round(r.Area)))
    except Exception:
        pass
hits.sort(key=lambda h: (h[2], h[0]))
L.append('rooms matching %s : %d' % (want, len(hits)))
for nm, i, lv, x, y, a in hits[:40]:
    L.append('  %-16s %-9s %-18s (%8.1f,%8.1f) %5d SF' % (nm, i, lv, x, y, a))
if hits:
    xs = [h[3] for h in hits]; ys = [h[4] for h in hits]
    L.append('extent of matches: x %.1f..%.1f  y %.1f..%.1f' % (min(xs), max(xs), min(ys), max(ys)))
result = '\n'.join(L)

# Search text notes + sheet/project params for a string. args {"q":"Keeler"}
from Autodesk.Revit.DB import TextNote, ViewSheet, StorageType, BuiltInCategory
q = args.get('q', 'Keeler').lower()
L = []
seen = set()
for tn in FilteredElementCollector(doc).OfClass(TextNote):
    try:
        t = tn.Text or ''
        if q in t.lower():
            s = ' | '.join(x.strip() for x in t.splitlines() if x.strip())
            if s not in seen:
                seen.add(s)
                v = doc.GetElement(tn.OwnerViewId)
                L.append('TEXT in %s : %s' % ((v.Name if v else '?')[:24], s[:420]))
    except Exception: pass
pi = doc.ProjectInformation
for p in pi.Parameters:
    try:
        if p.StorageType == StorageType.String and p.AsString() and q in p.AsString().lower():
            L.append('PROJINFO %-22s : %s' % (p.Definition.Name, p.AsString().replace('\n', ' | ')))
    except Exception: pass
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    try:
        if q in (s.Name or '').lower():
            L.append('SHEET %-8s : %s' % (s.SheetNumber, s.Name))
    except Exception: pass
result = '\n'.join(L[:25]) or 'no matches'

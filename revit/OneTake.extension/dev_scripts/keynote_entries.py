from Autodesk.Revit.DB import KeynoteTable, KeyBasedTreeEntry
kt = KeynoteTable.GetKeynoteTable(doc)
ents = kt.GetKeyBasedTreeEntries()
L = []
try:
    n = ents.Count
except Exception:
    n = None
L.append('entries container: %s  Count=%s' % (type(ents).__name__, n))
rows = []
try:
    for e in ents:
        rows.append((e.Key, e.ParentKey, e.KeynoteText))
except Exception as ex:
    L.append('iterate failed: %s' % str(ex)[:70])
L.append('total rows: %d' % len(rows))
want = ('SHINGLE', 'STUCCO', 'SLAB', 'GYP', 'WEEP', 'BOTTOM PLATE', 'TOP PLATE',
        'STUD', 'TRUSS', 'BATT', 'FOOTING', 'INSULATION')
L.append('--- rows whose text matches the KEYNOTES SECTION legend')
for k, p, t in rows:
    u = (t or '').upper()
    if any(w in u for w in want):
        L.append('  key=%-16r parent=%-16r %s' % (k, p, (t or '')[:52]))
L.append('--- first 15 rows overall')
for k, p, t in rows[:15]:
    L.append('  key=%-16r parent=%-16r %s' % (k, p, (t or '')[:52]))
result = '\n'.join(L)

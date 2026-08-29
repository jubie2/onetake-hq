# Approved window schedule columns are: Mark, Count, Description, Level, Width,
# Height, Sill Height, U Factor, SHGC, Comments - no Manufacturer / Model.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSchedule
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
HIDE = ('Manufacturer', 'Model')
WIDTH = {'Mark': 0.05, 'Count': 0.045, 'Description': 0.07, 'Level': 0.095,
         'Height': 0.06, 'Width': 0.06, 'Sill Height': 0.07, 'Comments': 0.06,
         'U- FACTOR': 0.06, 'SHGC': 0.05}
L = []
t = Transaction(pdoc, 'OneTake: window schedule columns'); _prep(t); t.Start()
for vs in FEC(pdoc).OfClass(ViewSchedule):
    if vs.Name != 'WINDOWS SCHEDULE': continue
    sd = vs.Definition
    tot = 0.0
    for i in range(sd.GetFieldCount()):
        f = sd.GetField(i)
        n = f.GetName()
        if n in HIDE:
            f.IsHidden = True
            L.append('  hid %s' % n)
            continue
        f.IsHidden = False
        if n in WIDTH:
            try: f.GridColumnWidth = WIDTH[n]
            except Exception: pass
        try: tot += f.GridColumnWidth
        except Exception: pass
    L.append('  visible width %.3f ft' % tot)
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)

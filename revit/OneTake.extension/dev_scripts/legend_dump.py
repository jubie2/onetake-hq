# Dump the text in the legend / notes views so we know the numbering per sheet.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
NAMES = args.get('views', [])
L = []
for nm in NAMES:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None:
        L.append('=== %s NOT FOUND' % nm); continue
    txts = []
    for t2 in FEC(doc, v.Id).OfClass(TextNote):
        s = (t2.Text or '').replace('\r', ' ').replace('\n', ' ').strip()
        if s: txts.append((t2.Coord.Y, t2.Coord.X, s))
    txts.sort(key=lambda z: (-z[0], z[1]))
    cnt = {}
    for e in FEC(doc, v.Id):
        k = e.Category.Name if e.Category else '(none)'
        cnt[k] = cnt.get(k, 0) + 1
    L.append('=== %s  (%d text notes)  cats: %s' % (nm, len(txts), cnt))
    for y, x, s in txts[:40]:
        L.append('    %s' % s[:96])
result = '\n'.join(L)

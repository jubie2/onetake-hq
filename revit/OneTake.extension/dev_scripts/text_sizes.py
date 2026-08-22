# Report text type sizes + what type existing roof-plan notes use.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, TextNoteType, TextNote, View,
                               BuiltInParameter as BIP)
L = ['--- sizes of candidate types (paper inches)']
for t in FEC(doc).OfClass(TextNoteType):
    n = t.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
    if not (n.startswith('ARCH TEXT') or 'Arial' in n): continue
    if n.startswith('AIA'): continue
    p = t.get_Parameter(BIP.TEXT_SIZE)
    L.append('  %-22s %.4f ft = %.3f in' % (n, p.AsDouble(), p.AsDouble() * 12))
L.append('--- types used by notes already in the ROOF LEGEND / main roof plan')
seen = {}
for vname in ('ROOF LEGEND',):
    for v in FEC(doc).OfClass(View):
        if v.IsTemplate or v.Name != vname: continue
        for tn in FEC(doc, v.Id).OfClass(TextNote):
            tt = doc.GetElement(tn.GetTypeId())
            nm2 = tt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
            sz = tt.get_Parameter(BIP.TEXT_SIZE).AsDouble() * 12
            seen[nm2] = (sz, (tn.Text or '')[:34].replace('\n', ' '))
for k in seen:
    L.append('  %-22s %.3f in  e.g. %r' % (k, seen[k][0], seen[k][1]))
result = '\n'.join(L)

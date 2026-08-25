# Read/write per-sheet titleblock fields. args {"sheets":[...], "set":{"Drawn By":"FRANCIS N."}, "dry":true}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, StorageType
dry = args.get('dry', True)
SET = args.get('set', {})
L = []
t = None
if not dry and SET:
    t = Transaction(doc, 'OneTake: sheet fields'); _prep(t); t.Start()
for s in sorted(FEC(doc).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
    if s.SheetNumber not in args['sheets']: continue
    row = []
    for pn in ('Drawn By', 'Checked By', 'Designed By', 'Approved By', 'Sheet Issue Date'):
        p = s.LookupParameter(pn)
        if p is None: continue
        v = p.AsString() or ''
        if pn in SET and not p.IsReadOnly:
            if not dry: p.Set(SET[pn])
            row.append('%s: %r -> %r' % (pn, v, SET[pn]))
        else:
            row.append('%s: %r' % (pn, v))
    L.append('%-6s %s' % (s.SheetNumber, '; '.join(row)))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)

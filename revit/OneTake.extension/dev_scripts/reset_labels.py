# Reset viewport title offsets to default on given sheets. args {"sheets":["ADU-2"],"dry":false}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, XYZ as _XYZ
L = []
want = set(args.get('sheets', []))
dry = args.get('dry', False)
t = None
if not dry:
    t = Transaction(doc, 'OneTake: reset titles'); _prep(t); t.Start()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber not in want: continue
    for vpid in s.GetAllViewports():
        vp = doc.GetElement(vpid)
        v = doc.GetElement(vp.ViewId)
        try:
            o = vp.LabelOffset
            L.append('%-8s %-26s label offset (%.2f, %.2f)' % (s.SheetNumber, v.Name[:26], o.X, o.Y))
            if not dry:
                vp.LabelOffset = _XYZ(0, 0, 0)
        except Exception as ex:
            L.append('%-8s %-26s ERR %s' % (s.SheetNumber, v.Name[:26], str(ex)[:50]))
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)

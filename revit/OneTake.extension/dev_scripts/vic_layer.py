from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, ImageInstance
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
L = []
t = Transaction(doc, 'OneTake: image draw layer'); _prep(t); t.Start()
for e in FEC(doc, sh.Id).OfClass(ImageInstance):
    p = e.LookupParameter('Draw Layer')
    if p and not p.IsReadOnly:
        old = p.AsInteger()
        p.Set(0)
        L.append('%s Draw Layer %s -> 0' % (e.Id, old))
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'none'

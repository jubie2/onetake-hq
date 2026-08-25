from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, TextNote, BuiltInParameter as BIP
L = []
t = Transaction(doc, 'OneTake: add ZIP'); _prep(t); t.Start()
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
for tn in FEC(doc, sh.Id).OfClass(TextNote):
    txt = tn.Text or ''
    if 'San Diego, CA' in txt and '92113' not in txt and len(txt) < 80:
        tn.Text = txt.replace('San Diego, CA', 'San Diego, CA 92113')
        L.append('sheet text %s: ZIP added' % tn.Id)
p = doc.ProjectInformation.get_Parameter(BIP.PROJECT_ADDRESS)
if p and '92113' not in (p.AsString() or ''):
    p.Set('4439 Keeler Ave.\nSan Diego, CA 92113')
    L.append('Project Address -> 4439 Keeler Ave. / San Diego, CA 92113')
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'nothing changed'

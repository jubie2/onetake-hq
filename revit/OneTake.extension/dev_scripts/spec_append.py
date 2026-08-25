from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
rv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - Roof Plan': rv = v; break
L = []
t = Transaction(doc, 'OneTake: shingle spec'); _prep(t); t.Start()
for tn in FEC(doc, rv.Id).OfClass(TextNote):
    txt = tn.Text or ''
    if txt.startswith("CLASS 'A' ROOF SHINGLES") and 'OWENS' not in txt:
        tn.Text = txt.rstrip() + " - OWENS CORNING (OR EQ.), ICC-ESR LISTED / CRRC RATED"
        L.append('appended to %s' % tn.Id)
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'not found'

# Update stale code years in the ELECTRICAL LEGEND notes. args {"dry":true}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
dry = args.get('dry', True)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ELECTRICAL LEGEND': v = x; break
SUBS = [
 ('2005  NATIONAL ELECTRICAL CODES', '2023 NATIONAL ELECTRICAL CODE (NEC)'),
 ('2005 NATIONAL ELECTRICAL CODES', '2023 NATIONAL ELECTRICAL CODE (NEC)'),
 ('2005 NEC AS AMENDED BY THE 2007 CALIFORNIA ELECTRICAL CODE',
  '2023 NEC AS AMENDED BY THE 2022 CALIFORNIA ELECTRICAL CODE'),
]
L = []
t = None
if not dry:
    t = Transaction(doc, 'OneTake: elec codes'); _prep(t); t.Start()
for e in FEC(doc, v.Id).OfClass(TextNote):
    txt = e.Text or ''
    new = txt
    for a, b in SUBS:
        if a in new: new = new.replace(a, b)
    if new != txt:
        L.append('id %s: updating' % e.Id.Value)
        if not dry: e.Text = new
    elif '2005' in txt or '2007' in txt:
        L.append('id %s: STILL HAS 2005/2007: %s' % (e.Id.Value,
                 txt[max(0, txt.find('2005') - 40):txt.find('2005') + 60].replace('\r', ' ')))
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'nothing matched'

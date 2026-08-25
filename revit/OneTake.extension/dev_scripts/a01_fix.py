# Fix the stale Logan Ave content on the A01 title page. args {"dry":true}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, TextNote
dry = args.get('dry', True)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A01': sh = s; break
# match by leading text -> full replacement
FIX = [
 ('John Vo Residence', '4439 Keeler Ave ADU'),
 ('4367#1-4367#2 Logan Ave', '4439 Keeler Ave.\nSan Diego, CA'),
 ('EXISTING 5 UNIT APARTMENT',
  'PROPOSED NEW DETACHED TWO-STORY ADU,\n637 SF PER FLOOR / 1,274 SF TOTAL,\nON SINGLE FAMILY LOT'),
 ('BUILDING ANALYSIS',
  'BUILDING ANALYSIS:\n\nEXISTING RESIDENCE BLDG-1 (E) SINGLE FAMILY RESIDENCE\n'
  '\nPROPOSED NEW ADU (TWO STORY):\n\t\t1st FLOOR:\t637 SF\n\t\t2nd FLOOR:\t637 SF\n'
  '\t\tTOTAL ADU AREA:\t1,274 SF'),
]
L = []
t = None
if not dry:
    t = Transaction(doc, 'OneTake: fix A01 title page'); _prep(t); t.Start()
for tn in FEC(doc, sh.Id).OfClass(TextNote):
    txt = (tn.Text or '').strip()
    for lead, new in FIX:
        if txt.startswith(lead):
            L.append('MATCH %s: %r -> %r' % (tn.Id, txt[:45], new[:45]))
            if not dry:
                tn.Text = new
# PROJECT DATA note: fill the blanks, keep the correct legal/zone/parcel
for tn in FEC(doc, sh.Id).OfClass(TextNote):
    txt = tn.Text or ''
    if txt.startswith('PROJECT NAME'):
        new = txt.replace('PROJECT NAME:  -', 'PROJECT NAME: \t4439 Keeler Ave ADU')
        new = new.replace('\t-\t\t\t\t\t', '\tNguyen Minh Duy\t\t\t\t')
        L.append('PROJECT DATA %s: name/owner filled (changed=%s)' % (tn.Id, new != txt))
        if not dry and new != txt:
            tn.Text = new
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'no matches'

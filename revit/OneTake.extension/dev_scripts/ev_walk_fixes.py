# Walkthrough fixes vs the approved set:
#  1. show the section / elevation reference bubbles on both floor plans
#  2. add U-Factor + SHGC columns to the window schedule (approved A101 carries them)
#  3. add a mini-split equipment schedule to A200 (approved has a FURNACE UNIT SCHEDULE;
#     ours specifies mini-splits in the keynotes with no equipment data)
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Category,
                               ViewSchedule, ViewSheet, TextNote, TextNoteOptions,
                               TextNoteType, HorizontalTextAlignment, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = []
t = Transaction(pdoc, 'OneTake: walkthrough fixes'); _prep(t); t.Start()
# --- 1. section / elevation marks back on the floor plans ---
for vid, nm in ((718579, '1st Floor Plan'), (1715860, '2nd FLoor Level')):
    v = pdoc.GetElement(ElementId(vid))
    for bic, cn in ((BIC.OST_Sections, 'Sections'), (BIC.OST_Elev, 'Elevations')):
        c = Category.GetCategory(pdoc, bic)
        try:
            v.SetCategoryHidden(c.Id, False)
            L.append('  %s: %s shown' % (nm, cn))
        except Exception as ex:
            L.append('  %s: %s FAIL %s' % (nm, cn, str(ex)[:40]))
pdoc.Regenerate()
# --- 2. Title-24 columns on the window schedule ---
for vs in FEC(pdoc).OfClass(ViewSchedule):
    if vs.Name != 'WINDOWS SCHEDULE': continue
    sd = vs.Definition
    have = set()
    for i in range(sd.GetFieldCount()):
        have.add(sd.GetField(i).GetName())
    for want in ('U- FACTOR', 'SHGC'):
        if want in have: L.append('  window schedule already has %s' % want); continue
        added = False
        for sf in sd.GetSchedulableFields():
            try:
                if sf.GetName(pdoc) == want:
                    sd.AddField(sf); added = True; break
            except Exception: pass
        L.append('  window schedule + %s : %s' % (want, 'ok' if added else 'FIELD NOT FOUND'))
pdoc.Regenerate()
# --- 3. mini-split equipment schedule note on A200 ---
tt = None
for x in FEC(pdoc).OfClass(TextNoteType):
    n = x.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
    if '3/32' in n: tt = x; break
if tt is None:
    for x in FEC(pdoc).OfClass(TextNoteType):
        n = x.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        if '1/8' in n: tt = x; break
if tt is None: tt = FEC(pdoc).OfClass(TextNoteType).FirstElement()
sh = None
for s in FEC(pdoc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200': sh = s
exists = False
for e in FEC(pdoc, sh.Id).OfClass(TextNote):
    if 'MINI-SPLIT' in (e.Text or '').upper(): exists = True
if not exists:
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    txt = ('DUCTLESS MINI-SPLIT SYSTEM SCHEDULE\r'
           'MARK\tSYSTEM\t\tSERVES\t\tNOM. CAP.\tSEER2 / HSPF2\r'
           'MS-1\tHEAT PUMP - OUTDOOR\t1ST FLOOR (3 ZONES)\t24,000 BTUH\t18.0 / 8.5 MIN.\r'
           'MS-2\tHEAT PUMP - OUTDOOR\t2ND FLOOR (3 ZONES)\t24,000 BTUH\t18.0 / 8.5 MIN.\r'
           'FC-1..6\tWALL-MTD FAN COIL\tPER PLAN\t\t9,000 BTUH EA.\t-\r\r'
           'CAPACITIES AND EFFICIENCIES TO BE CONFIRMED BY THE TITLE-24\r'
           'ENERGY REPORT PRIOR TO EQUIPMENT PURCHASE.')
    TextNote.Create(pdoc, sh.Id, _XYZ(0.60, 0.62, 0), txt, o)
    L.append('  A200 + mini-split equipment schedule')
else:
    L.append('  A200 mini-split schedule already present')
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)

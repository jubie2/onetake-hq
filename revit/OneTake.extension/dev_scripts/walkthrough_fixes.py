# Final-walkthrough fixes: Keeler fixture table on A02, park stale Title-24 sheets,
# hide stale landscape sheets from the sheet list.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               BuiltInParameter as BIP)
NEWTABLE = (
 'TOTAL PLUMBING FIXTURE CALCULATION\n\n'
 'EXISTING RESIDENCE (BLDG-1):\n'
 '  (1) Lavatory\n  (1) Kitchen Sink\n  (1) Shower\n  (1) Water Closet\n'
 '  (1) Clothes Washer\n\n'
 'PROPOSED ADU (BLDG-2) - UNIT 1, 1ST FLOOR:\n'
 '  (2) Lavatory\n  (1) Kitchen Sink\n  (1) Shower\n  (1) Water Closet\n'
 '  (1) Clothes Washer\n\n'
 'PROPOSED ADU (BLDG-2) - UNIT 2, 2ND FLOOR:\n'
 '  (2) Lavatory\n  (1) Kitchen Sink\n  (1) Shower\n  (1) Water Closet\n'
 '  (1) Clothes Washer')
L = []
t = Transaction(doc, 'OneTake: walkthrough fixes'); _prep(t); t.Start()
e = doc.GetElement(ElementId(2148238))
e.Text = NEWTABLE
L.append('A02 fixture table rewritten')
for s in FEC(doc).OfClass(ViewSheet):
    n = s.SheetNumber
    if n in ('A106', 'A107', 'A108', 'A109', 'A110'):
        s.SheetNumber = 'X-' + n
        p = s.get_Parameter(BIP.SHEET_SCHEDULED)
        if p and not p.IsReadOnly: p.Set(0)
        L.append('parked %s (%s)' % (n, s.Name))
    elif n in ('L1', 'L2', 'L3', 'L22', 'L33'):
        p = s.get_Parameter(BIP.SHEET_SCHEDULED)
        if p and not p.IsReadOnly: p.Set(0)
        L.append('hidden from index: %s (%s)' % (n, s.Name))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

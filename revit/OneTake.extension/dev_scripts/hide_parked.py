# Un-check "Appears In Sheet List" for parked X-* sheets.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               BuiltInParameter as BIP)
t = Transaction(doc, 'OneTake: hide parked sheets'); _prep(t); t.Start()
n = 0
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber.startswith('X-'):
        p = s.get_Parameter(BIP.SHEET_SCHEDULED)
        if p and not p.IsReadOnly:
            p.Set(0); n += 1
doc.Regenerate(); t.Commit()
result = 'hidden from sheet list: %d' % n

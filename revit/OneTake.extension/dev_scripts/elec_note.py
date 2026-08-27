# Add a superseding electrical code note on ADU-6 (the DWG legend cites 2005/2007).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, TextNote,
                               TextNoteOptions, TextNoteType, HorizontalTextAlignment,
                               BuiltInParameter as BIP, XYZ as _XYZ)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'ADU-6': sh = s; break
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
t = Transaction(doc, 'OneTake: elec code note'); _prep(t); t.Start()
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Left
TextNote.Create(doc, sh.Id, _XYZ(0.30, 0.52, 0), 0.85,
    'ELECTRICAL CODE NOTE:\n'
    'ALL ELECTRICAL WORK SHALL COMPLY WITH THE 2023 NEC AS ADOPTED AND AMENDED BY THE '
    '2022 CALIFORNIA ELECTRICAL CODE (CEC) AND CITY OF SAN DIEGO AMENDMENTS. WHERE THE '
    'GENERAL NOTES ABOVE REFERENCE EARLIER CODE EDITIONS (2005 NEC / 2007 CEC), THE '
    'CURRENT ADOPTED CODES GOVERN.', o)
doc.Regenerate(); t.Commit()
result = 'note added to ADU-6'

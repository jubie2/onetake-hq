# Put text on a sheet. args {"items":[{"sheet":"ADU-2","at":[1.05,0.98],"text":"..."}], "size_in":0.25}
from Autodesk.Revit.DB import (ViewSheet, TextNote, TextNoteType, ElementTypeGroup, XYZ as _XYZ,
                               FilteredElementCollector as FEC, BuiltInParameter)
L = []
t = Transaction(doc, 'OneTake: sheet text'); _prep(t); t.Start()
tnt = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
for it in args['items']:
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == it['sheet']: sh = s; break
    if sh is None:
        L.append('%s not found' % it['sheet']); continue
    tn = TextNote.Create(doc, sh.Id, _XYZ(float(it['at'][0]), float(it['at'][1]), 0), it['text'], tnt)
    L.append('%s: "%s" at (%.2f, %.2f)' % (it['sheet'], it['text'][:34], it['at'][0], it['at'][1]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

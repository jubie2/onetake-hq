from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, ElementId,
                               TextNoteType, TextNoteOptions, HorizontalTextAlignment,
                               BuiltInParameter as BIP, XYZ as _XYZ)
from System.Collections.Generic import List
fv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - Roof Framing Plan': fv = v; break
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
KILL = ('ROOF FRAMING NOTE', 'ROOF TRUSS MANUFACTURER', 'TRUSS SPACING', 'HEEL HEIGHT', 'TAIL LENGTH')
L = []
t = Transaction(doc, 'OneTake: framing note fix'); _prep(t); t.Start()
kill = [tn.Id for tn in FEC(doc, fv.Id).OfClass(TextNote)
        if any((tn.Text or '').startswith(k) for k in KILL)]
if kill: doc.Delete(List[ElementId](kill)); L.append('removed %d' % len(kill))
tf = fv.CropBox.Transform; inv = tf.Inverse
LINES = ['ROOF FRAMING NOTE: TRUSS MFR. PER DEFERRED SUBMITTAL',
         'TRUSS SPACING: 24" O.C. / HEEL HEIGHT: 3 15/16" U.N.O.',
         'TAIL LENGTH: 24" U.N.O. / TAIL SIZE: 2x4 U.N.O.']
for i, s in enumerate(list(reversed(LINES))):
    q = inv.OfPoint(_XYZ(1150.7 - i * 1.4, -151.8, 0.0))
    p = tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    TextNote.Create(doc, fv.Id, p, s, o)
L.append('placed 3 consolidated lines')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

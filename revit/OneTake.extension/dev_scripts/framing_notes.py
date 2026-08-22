# Restack the framing notes at a position proven visible, and report what each view holds.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, ElementId,
                               TextNoteType, TextNoteOptions, HorizontalTextAlignment,
                               BuiltInParameter as BIP, BuiltInCategory as BIC, XYZ as _XYZ,
                               CurveElement)
from System.Collections.Generic import List
WX0, WX1, WY0, WY1 = 1157.9, 1186.5, -150.3, -125.7
NOTES = {
 'ADU - Foundation Plan': [
   '15" x 12" CONT. CONC. FOOTING W/ (2) #4 CONT. TOP & BOTTOM,',
   'TYP. AT ALL EXTERIOR WALLS - FOUNDATION PER DETAIL ON SD1',
   '4" MIN. CONC. SLAB ON GRADE OVER 6 MIL VAPOR BARRIER',
   'OVER 4" SAND - #4 @ 18" O.C. EACH WAY'],
 'ADU - 2nd Floor Framing Plan': [
   '2x10 D.F. #2 FLOOR JOISTS @ 16" O.C.',
   'SPAN AS SHOWN - SEE DETAIL ON SD1',
   'BEARING WALL BELOW AT MID-SPAN'],
 'ADU - Roof Framing Plan': [
   'PRE-ENGINEERED ROOF TRUSSES @ 24" O.C.',
   'PER TRUSS MFR. CALCS - 5:12 PITCH',
   'TRUSS TIE-DOWN PER DETAIL ON SD1'],
}
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
L = []
t = Transaction(doc, 'OneTake: framing notes'); _prep(t); t.Start()
for nm, lines in NOTES.items():
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    kill = [e.Id for e in FEC(doc, v.Id).OfClass(TextNote)]
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
    for i, txt in enumerate(list(reversed(lines))):
        q = inv.OfPoint(_XYZ(WX0 - 1.6 - i * 1.4, WY0 - 1.5, 0.0))
        p = tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Left
        TextNote.Create(doc, v.Id, p, txt, o)
    doc.Regenerate()
    nl = len(list(FEC(doc, v.Id).OfClass(CurveElement)))
    nt = len(list(FEC(doc, v.Id).OfClass(TextNote)))
    L.append('%-30s detail curves %3d, notes %d' % (nm[:30], nl, nt))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

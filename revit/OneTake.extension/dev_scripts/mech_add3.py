# FAU-1 (dashed, in attic) + 24x24 return grille drawn on the 2nd floor mech plan;
# remove the keynote-13 tag from the 1st floor (return/FAU serve the attic level only).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               TextNoteOptions, TextNoteType, GraphicsStyle,
                               BuiltInParameter as BIP, HorizontalTextAlignment,
                               BuiltInCategory as BIC, ElementId, XYZ as _XYZ, Line)
from System.Collections.Generic import List
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
v2 = getview('ADU - 2nd Floor Mechanical Plan')
v1 = getview('ADU - 1st Floor Mechanical Plan')
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
L = []
t = Transaction(doc, 'OneTake: FAU + return grille'); _prep(t); t.Start()
def rect(view, cx, cy, hx, hy, dashed, diagonals):
    p = [(cx-hx, cy-hy), (cx+hx, cy-hy), (cx+hx, cy+hy), (cx-hx, cy+hy)]
    out = []
    for i in range(4):
        out.append(doc.Create.NewDetailCurve(view, Line.CreateBound(
            _XYZ(p[i][0], p[i][1], 0), _XYZ(p[(i+1)%4][0], p[(i+1)%4][1], 0))))
    if diagonals:
        out.append(doc.Create.NewDetailCurve(view, Line.CreateBound(
            _XYZ(p[0][0], p[0][1], 0), _XYZ(p[2][0], p[2][1], 0))))
        out.append(doc.Create.NewDetailCurve(view, Line.CreateBound(
            _XYZ(p[1][0], p[1][1], 0), _XYZ(p[3][0], p[3][1], 0))))
    if dashed and dash:
        for c in out:
            try: c.LineStyle = dash
            except Exception: pass
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Left
# FAU-1 in attic over the hall (dashed 2x4)
rect(v2, 1171.5, -140.5, 1.0, 2.0, True, False)
TextNote.Create(doc, v2.Id, _XYZ(1172.9, -142.4, 0), 'FAU-1', o)
# 24x24 return grille beside it
rect(v2, 1174.9, -140.3, 1.0, 1.0, False, True)
L.append('2nd: FAU-1 + return grille drawn')
# move keynote 13 next to the grille; delete the 1st-floor 13 tag
for e in FEC(doc, v2.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name == 'TAG LABEL':
            p = e.LookupParameter('TEXT')
            if p and p.AsString() == '13':
                e.Location.Move(_XYZ(1176.5 - e.Location.Point.X,
                                     -142.0 - e.Location.Point.Y, 0))
                L.append('2nd: 13 tag moved beside grille')
    except Exception: pass
kill = []
for e in FEC(doc, v1.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name == 'TAG LABEL':
            p = e.LookupParameter('TEXT')
            if p and p.AsString() == '13': kill.append(e.Id)
    except Exception: pass
if kill:
    doc.Delete(List[ElementId](kill))
    L.append('1st: removed %d stray 13 tag' % len(kill))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

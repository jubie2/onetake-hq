# List / delete the roof annotation I placed. args {"view":"ADU - Roof Plan","delete":false}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, CurveElement,
                               ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
TARGET = set(['5:12', 'RIDGE', 'EAVE, TYP.', 'EAVE'])
L = []; kill = []
for tn in FEC(doc, v.Id).OfClass(TextNote):
    txt = (tn.Text or '').strip()
    p = tn.Coord
    L.append('TEXT  %-8s %-12r at (%.1f, %.1f)' % (tn.Id, txt, p.X, p.Y))
    if txt in TARGET: kill.append(tn.Id)
for ce in FEC(doc, v.Id).OfClass(CurveElement):
    try:
        c = ce.GeometryCurve
        p0 = c.GetEndPoint(0); p1 = c.GetEndPoint(1)
        L.append('CURVE %-8s len %.2f (%.1f,%.1f)->(%.1f,%.1f)' % (
            ce.Id, c.Length, p0.X, p0.Y, p1.X, p1.Y))
        if c.Length < 12.0: kill.append(ce.Id)
    except Exception: pass
L.append('--- %d candidates to delete' % len(kill))
if args.get('delete') and kill:
    t = Transaction(doc, 'OneTake: clear roof notes'); _prep(t); t.Start()
    doc.Delete(List[ElementId](kill)); doc.Regenerate(); t.Commit()
    L.append('deleted %d' % len(kill))
result = '\n'.join(L)

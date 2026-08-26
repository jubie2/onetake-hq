# Renumber ADU door/window marks approved-style (doors 101+/201+, windows 01+/21+,
# counterclockwise from the entry), switch window tags to the instance-number family,
# and wipe the old drawn plan bubbles.  args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               TextNote, CurveElement, Arc, Line, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP,
                               ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
import re
dry = args.get('dry', True)
DOORS = [(2179234, '101'), (2169645, '102'), (2170093, '103'), (2162946, '104'),
         (2162300, '105'), (2170317, '106'), (2171965, '107'), (2171962, '108'),
         (2182211, '201'), (2182233, '202'), (2182232, '203'), (2182170, '204'),
         (2182173, '205'), (2182161, '206'), (2182160, '207'), (2182175, '208'),
         (2182199, '209'), (2182198, '210')]
WINS = [(2164986, '01'), (2179808, '02'), (2180657, '03'), (2164812, '04'),
        (2164844, '05'), (2164926, '06'), (2179883, '07'), (2179910, '08'),
        (2182167, '21'), (2182215, '22'), (2182229, '23'), (2182164, '24'),
        (2182165, '25'), (2182166, '26'), (2182216, '27'), (2182217, '28')]
L = []
wsym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_WindowTags):
    if s.Family.Name == 'Window Tag - Number': wsym = s; break
L.append('window number tag symbol: %s' % (wsym.Id.Value if wsym else 'MISSING'))
views = []
for nm in ('ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: views.append(x); break
# old drawn bubbles to wipe
kill = []
for v in views:
    arcs = []; lines = []; notes = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        if isinstance(e, CurveElement):
            c = e.GeometryCurve
            if isinstance(c, Arc) and abs(c.Radius - 0.55) < 0.05:
                arcs.append((e.Id, c.Center))
            elif isinstance(c, Line):
                lines.append((e.Id, c.GetEndPoint(0), c.GetEndPoint(1)))
        elif isinstance(e, TextNote):
            if re.match(r'^\s*\d{1,2}\s*$', (e.Text or '').replace('\r', ' ')):
                notes.append((e.Id, e.Coord))
    for aid, c in arcs: kill.append(aid)
    for nid, p in notes:
        if any(p.DistanceTo(c) < 1.5 for _, c in arcs): kill.append(nid)
    for lid, p0, p1 in lines:
        if any(min(p0.DistanceTo(c), p1.DistanceTo(c)) < 0.9 for _, c in arcs):
            kill.append(lid)
L.append('old bubbles to wipe: %d elems' % len(kill))
# window tags to retype
wtags = []
for v in views:
    for e in FEC(doc, v.Id).OfClass(IndependentTag):
        try:
            tt = doc.GetElement(e.GetTypeId())
            if tt.FamilyName == 'Window Tag' and wsym is not None:
                wtags.append(e.Id)
        except Exception: pass
L.append('window tags to switch to number type: %d' % len(wtags))
if not dry:
    t = Transaction(doc, 'OneTake: renumber marks'); _prep(t); t.Start()
    n = 0
    for eid, mk in DOORS + WINS:
        e = doc.GetElement(ElementId(eid))
        if e is None: L.append('  %s MISSING' % eid); continue
        p = e.get_Parameter(BIP.ALL_MODEL_MARK)
        p.Set(mk); n += 1
    if wsym is not None:
        if not wsym.IsActive:
            wsym.Activate(); doc.Regenerate()
        for tid in wtags:
            doc.GetElement(tid).ChangeTypeId(wsym.Id)
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate(); t.Commit()
    bad = []
    for eid, mk in DOORS + WINS:
        e = doc.GetElement(ElementId(eid))
        if e and e.get_Parameter(BIP.ALL_MODEL_MARK).AsString() != mk:
            bad.append(eid)
    L.append('set %d marks%s, retyped %d tags, wiped %d' % (
        n, ' BAD:%s' % bad if bad else ' (verified)', len(wtags), len(kill)))
result = '\n'.join(L)

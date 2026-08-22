# Assign the missing Type Mark and tag the ADU walls W1/W2/W3 per the Floor Plan Legend.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, View, FamilySymbol,
                               IndependentTag, Reference, TagOrientation, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, XYZ as _XYZ)
from System.Collections.Generic import List
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
# legend: W1 interior 2x4, W2 exterior 2x4, W3 exterior 2x6
ASSIGN = {'Generic - 6" NEW 2': 'W2'}
L = []
tag = None
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_WallTags): continue
        if s.Family.Name == 'Wall Tag' and \
           (s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == '1/4"':
            tag = s; break
    except Exception: pass
L.append('wall tag type: %s' % (tag.Id if tag else 'NOT FOUND'))
def tname(t):
    p = t.get_Parameter(BIP.SYMBOL_NAME_PARAM)
    return p.AsString() if p else str(t.Id)
VIEWS = ['ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan']
if not dry:
    t = Transaction(doc, 'OneTake: wall tags'); _prep(t); t.Start()
    if not tag.IsActive: tag.Activate()
    for wt in FEC(doc).OfClass(Wall):
        pass
    from Autodesk.Revit.DB import WallType
    for wt in FEC(doc).OfClass(WallType):
        n = tname(wt)
        if n in ASSIGN:
            p = wt.get_Parameter(BIP.ALL_MODEL_TYPE_MARK)
            if p and not p.IsReadOnly and (p.AsString() or '') != ASSIGN[n]:
                p.Set(ASSIGN[n]); L.append('  set Type Mark %s = %s' % (n, ASSIGN[n]))
    doc.Regenerate()
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    # one tag per distinct wall type, on the longest wall of that type
    best = {}
    for w in FEC(doc, v.Id).OfClass(Wall):
        try:
            b = w.get_BoundingBox(None)
            if b is None: continue
            cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
            if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
            wt = doc.GetElement(w.GetTypeId())
            mark = wt.get_Parameter(BIP.ALL_MODEL_TYPE_MARK)
            mk = mark.AsString() if mark else None
            if not mk: continue
            ln = w.Location.Curve.Length
            if mk not in best or ln > best[mk][1]:
                best[mk] = (w, ln, cx, cy)
        except Exception: pass
    L.append('%-24s tag: %s' % (nm, dict((k, '%.1f ft' % best[k][1]) for k in best)))
    if dry: continue
    n = 0
    for mk in best:
        w, ln, cx, cy = best[mk]
        c = w.Location.Curve
        mid = c.Evaluate(0.5, True)
        try:
            IndependentTag.Create(doc, tag.Id, v.Id, Reference(w), True,
                                  TagOrientation.Horizontal,
                                  _XYZ(mid.X + 2.5, mid.Y + 2.5, mid.Z))
            n += 1
        except Exception as ex:
            L.append('    %s fail %s' % (mk, str(ex)[:50]))
    L.append('    placed %d wall tags' % n)
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)

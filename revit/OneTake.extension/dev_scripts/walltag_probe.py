from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol, Wall, WallType,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, View,
                               IndependentTag)
L = ['=== wall tag families']
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_WallTags): continue
        L.append('  %s : %s' % (s.Family.Name, s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
    except Exception: pass
L.append('=== wall types used in the ADU + their Type Mark')
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
seen = {}
for w in FEC(doc).OfClass(Wall):
    try:
        b = w.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        t = doc.GetElement(w.GetTypeId())
        nmp = t.get_Parameter(BIP.SYMBOL_NAME_PARAM)
        tm = t.get_Parameter(BIP.WINDOW_TYPE_ID)
        tm2 = t.get_Parameter(BIP.ALL_MODEL_TYPE_MARK)
        k = nmp.AsString() if nmp else str(t.Id)
        if k in seen: continue
        seen[k] = 1
        L.append('  %-24s TypeMark=%r  function=%s' % (
            k, tm2.AsString() if tm2 else None, t.Function))
    except Exception as ex:
        L.append('  err %s' % str(ex)[:40])
L.append('=== does the main 1st Floor Plan carry wall tags?')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != '1st Floor Plan': continue
    n = 0
    for t2 in FEC(doc, v.Id).OfClass(IndependentTag):
        try:
            if t2.Category and 'Wall' in t2.Category.Name: n += 1
        except Exception: pass
    L.append('  wall tags on 1st Floor Plan: %d' % n)
result = '\n'.join(L)

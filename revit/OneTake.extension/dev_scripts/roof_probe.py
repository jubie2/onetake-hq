# Inspect roofs visible in a view + available annotation symbols. args {"view":"ADU - Roof Plan"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, RoofBase, FootPrintRoof,
                               BuiltInParameter as BIP, BuiltInCategory as BIC, FamilySymbol,
                               TextNoteType, ElementId, XYZ as _XYZ)
nm = args.get('view', 'ADU - Roof Plan')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s  scale %s' % (nm, v.Scale)]
bb = v.CropBox
L.append('crop local %.2f..%.2f x %.2f..%.2f' % (bb.Min.X, bb.Max.X, bb.Min.Y, bb.Max.Y))
tf = bb.Transform
c = []
for x in (bb.Min.X, bb.Max.X):
    for y in (bb.Min.Y, bb.Max.Y):
        c.append(tf.OfPoint(_XYZ(x, y, 0.0)))
L.append('crop world X %.1f..%.1f Y %.1f..%.1f' % (
    min(p.X for p in c), max(p.X for p in c), min(p.Y for p in c), max(p.Y for p in c)))
L.append('--- roofs in view')
for r in FEC(doc, v.Id).OfClass(RoofBase):
    b = r.get_BoundingBox(v)
    sl = r.get_Parameter(BIP.ROOF_SLOPE)
    L.append('id %s  %s' % (r.Id, r.Name if hasattr(r, 'Name') else '?'))
    if b:
        L.append('   world X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f' % (
            b.Min.X, b.Max.X, b.Min.Y, b.Max.Y, b.Min.Z, b.Max.Z))
    L.append('   slope param = %s' % (sl.AsDouble() if sl and sl.HasValue else 'none'))
    if isinstance(r, FootPrintRoof):
        try:
            mc = r.GetProfiles()
            n = 0
            for arr in mc:
                for m in arr:
                    cv = m.GetCurve()
                    p0 = cv.GetEndPoint(0); p1 = cv.GetEndPoint(1)
                    sd = r.get_DefinesSlope(m); ang = r.get_SlopeAngle(m) if sd else 0
                    L.append('   edge %d (%.1f,%.1f,%.1f)->(%.1f,%.1f,%.1f) slopeDef=%s rise/12=%.2f' % (
                        n, p0.X, p0.Y, p0.Z, p1.X, p1.Y, p1.Z, sd, ang * 12.0))
                    n += 1
        except Exception as ex:
            L.append('   profile ERR %s' % str(ex)[:60])
L.append('--- annotation symbols with "slope"/"arrow"/"ridge" in the name')
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        n = s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        f = s.Family.Name
        low = (f + ' ' + n).lower()
        if any(k in low for k in ('slope', 'arrow', 'ridge', 'pitch')):
            L.append('   %s : %s  (cat %s)' % (f, n, s.Category.Name if s.Category else '?'))
    except Exception: pass
L.append('--- text note types')
for tt in FEC(doc).OfClass(TextNoteType):
    try: L.append('   %s' % tt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
    except Exception: pass
result = '\n'.join(L)

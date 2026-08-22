from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ImportInstance, View, ElementId)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = ['=== which rooms the small windows (36, 44) serve']
ph = None
for p in doc.Phases:
    ph = p
for e in FEC(doc).OfCategory(BIC.OST_Windows).WhereElementIsNotElementType():
    try:
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        m = mk.AsString() if mk else ''
        if m not in ('36', '44', '30', '34', '39', '42'): continue
        b = e.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        names = []
        for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
            try:
                if r.Area < 1: continue
                rb = r.get_BoundingBox(None)
                if rb is None: continue
                if (rb.Min.X - 1.2 <= cx <= rb.Max.X + 1.2 and rb.Min.Y - 1.2 <= cy <= rb.Max.Y + 1.2
                        and rb.Min.Z - 1 <= b.Min.Z <= rb.Max.Z + 1):
                    names.append(r.get_Parameter(BIP.ROOM_NAME).AsString())
            except Exception: pass
        L.append('  mark %-3s at (%.1f,%.1f) z %.1f -> rooms %s' % (m, cx, cy, b.Min.Z, names))
    except Exception: pass
L.append('=== content on the code/energy sheets')
for sn in ('A04', 'A05', 'A06', 'A106', 'A107', 'A108', 'A109', 'A110', 'A301', 'AD1', 'SD0', 'SD3', 'A03'):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber != sn: continue
        n_all = 0; imgs = 0; imports = 0
        for e in FEC(doc, s.Id):
            n_all += 1
            cn = e.Category.Name if e.Category else ''
            if cn == 'Raster Images': imgs += 1
            if isinstance(e, ImportInstance): imports += 1
        L.append('  %-6s %-32s elements %3d  raster images %2d  imports %d' % (
            sn, s.Name[:32], n_all, imgs, imports))
result = '\n'.join(L)

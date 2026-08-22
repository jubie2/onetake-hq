from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, View, Dimension)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = ['=== every ADU window mapped to its room']
rooms = []
for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
    try:
        if r.Area < 1: continue
        rb = r.get_BoundingBox(None)
        if rb is None: continue
        cx = (rb.Min.X + rb.Max.X) / 2.0; cy = (rb.Min.Y + rb.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        rooms.append((r.get_Parameter(BIP.ROOM_NAME).AsString(), rb, r.Level.Name))
    except Exception: pass
byroom = {}
for e in FEC(doc).OfCategory(BIC.OST_Windows).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        w = e.Symbol.get_Parameter(BIP.WINDOW_WIDTH).AsDouble()
        h = e.Symbol.get_Parameter(BIP.WINDOW_HEIGHT).AsDouble()
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        for nm, rb, lv in rooms:
            if (rb.Min.X - 1.2 <= cx <= rb.Max.X + 1.2 and rb.Min.Y - 1.2 <= cy <= rb.Max.Y + 1.2
                    and rb.Min.Z - 1 <= b.Min.Z <= rb.Max.Z + 1):
                k = '%s / %s' % (lv[:12], nm)
                byroom.setdefault(k, []).append('%s(%.1fsf)' % (mk.AsString() if mk else '?', w * h))
    except Exception: pass
for k in sorted(byroom): L.append('  %-28s %s' % (k, ', '.join(byroom[k])))
for nm, rb, lv in rooms:
    k = '%s / %s' % (lv[:12], nm)
    if k not in byroom and nm in ('Bed-1', 'Bed-2'):
        L.append('  %-28s NO WINDOW FOUND' % k)
L.append('=== dimensions in the Site view near the ADU (setbacks?)')
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name != 'Site': continue
    n = 0; near = 0
    for d in FEC(doc, v.Id).OfClass(Dimension):
        n += 1
        try:
            o = d.Origin
            if X0 - 40 <= o.X <= X1 + 40 and Y0 - 40 <= o.Y <= Y1 + 40: near += 1
        except Exception: pass
    L.append('  Site view: %d dimensions total, %d within 40 ft of the ADU' % (n, near))
    txt = 0
    for t2 in FEC(doc, v.Id).OfCategory(BIC.OST_TextNotes):
        txt += 1
    L.append('  Site view: %d text notes' % txt)
result = '\n'.join(L)

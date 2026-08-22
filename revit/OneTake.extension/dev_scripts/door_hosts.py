from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, Wall)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for e in FEC(doc).OfCategory(BIC.OST_Doors).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        lv = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else '?'
        if lv != '1st Floor Level': continue
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        h = e.Host
        hn = '(none)'
        if h is not None:
            try: hn = '%s %s' % (h.Category.Name, h.WallType.Function if isinstance(h, Wall) else '')
            except Exception: hn = str(h.Id)
        tn = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
        L.append('  mark %-4s %-12s at (%.1f,%.1f)  host=%s' % (
            mk.AsString() if mk else '?', tn, cx, cy, hn))
    except Exception as ex:
        L.append('  err %s' % str(ex)[:40])
result = '\n'.join(L)

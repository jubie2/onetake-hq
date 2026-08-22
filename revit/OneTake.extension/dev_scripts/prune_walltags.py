# Drop wall tags whose host wall sits outside the ADU wall rectangle.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag, Wall,
                               ElementId, BuiltInParameter as BIP)
from System.Collections.Generic import List
WX0, WX1, WY0, WY1 = 1157.9, 1186.5, -150.3, -125.7
L = []
kill = []
for nm in ('ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    for t2 in FEC(doc, v.Id).OfClass(IndependentTag):
        try:
            if not (t2.Category and 'Wall' in t2.Category.Name): continue
            for hid in t2.GetTaggedLocalElementIds():
                w = doc.GetElement(hid)
                if not isinstance(w, Wall): continue
                b = w.get_BoundingBox(None)
                cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
                inside = (WX0 - 1 <= cx <= WX1 + 1 and WY0 - 1 <= cy <= WY1 + 1)
                tm = doc.GetElement(w.GetTypeId()).get_Parameter(BIP.ALL_MODEL_TYPE_MARK)
                L.append('%-22s tag %s -> %s at (%.1f,%.1f) inside=%s' % (
                    nm[6:], tm.AsString() if tm else '?', w.Id, cx, cy, inside))
                if not inside: kill.append(t2.Id)
        except Exception: pass
if kill and not args.get('dry', True):
    t = Transaction(doc, 'OneTake: prune wall tags'); _prep(t); t.Start()
    doc.Delete(List[ElementId](kill)); doc.Regenerate(); t.Commit()
    L.append('deleted %d off-building tags' % len(kill))
result = '\n'.join(L)

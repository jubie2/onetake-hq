# Delete short wall stubs in a region (trace noise). args {"region":[x0,y0,x1,y1], "max_len":2.5, "level":"1st Floor Level", "dry":true}
from Autodesk.Revit.DB import Wall, Level, TransactionGroup
reg = args['region']; mx = float(args.get('max_len', 2.5))
lvl = args.get('level')
victims = []
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        c = w.Location.Curve
        p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
        if not all(reg[0] <= p.X <= reg[2] and reg[1] <= p.Y <= reg[3] for p in (p0, p1)):
            continue
        if lvl:
            l = doc.GetElement(w.LevelId)
            if l is None or l.Name != lvl: continue
        if c.Length <= mx:
            victims.append((w.Id.Value, round(c.Length, 2), round(p0.X, 1), round(p0.Y, 1)))
    except Exception:
        pass
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: clean stubs'); _prep(t); t.Start()
    for vid, L, x, y in victims:
        try: doc.Delete(ElementId(long(vid)))
        except Exception: pass
    t.Commit()
result = {'count': len(victims), 'deleted': not args.get('dry', True), 'walls': victims[:40]}

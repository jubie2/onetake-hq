# Delete all walls of a level inside a region. args {"region":[x0,y0,x1,y1],"level":"...","dry":true}
from Autodesk.Revit.DB import Wall
reg = args['region']; lvl = args.get('level')
ids = []
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        c = w.Location.Curve; p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
        if not all(reg[0] <= p.X <= reg[2] and reg[1] <= p.Y <= reg[3] for p in (p0, p1)): continue
        if lvl:
            l = doc.GetElement(w.LevelId)
            if l is None or l.Name != lvl: continue
        ids.append(w.Id)
    except Exception: pass
if not args.get('dry', True) and ids:
    t = Transaction(doc, 'OneTake: clear region'); _prep(t); t.Start()
    for i in ids:
        try: doc.Delete(i)
        except Exception: pass
    t.Commit()
result = {'count': len(ids), 'deleted': not args.get('dry', True)}

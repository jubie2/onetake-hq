# Delete walls AND their hosted doors/windows in a region, on given levels.
# args {"region":[x0,y0,x1,y1], "levels":["1st Floor Level","2nd FLoor Level"], "dry":true}
from Autodesk.Revit.DB import Wall, FamilyInstance, BuiltInCategory
reg = args['region']; levels = set(args.get('levels', []))
def inreg(p): return reg[0] <= p.X <= reg[2] and reg[1] <= p.Y <= reg[3]
wall_ids, host_ids = [], []
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        l = doc.GetElement(w.LevelId)
        if levels and (l is None or l.Name not in levels): continue
        c = w.Location.Curve
        if not (inreg(c.GetEndPoint(0)) and inreg(c.GetEndPoint(1))): continue
        wall_ids.append(w.Id)
    except Exception: pass
for cat in (BuiltInCategory.OST_Doors, BuiltInCategory.OST_Windows):
    for fi in FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType():
        try:
            l = doc.GetElement(fi.LevelId)
            if levels and (l is None or l.Name not in levels): continue
            bb = fi.get_BoundingBox(None)
            if bb is None: continue
            c = (bb.Min + bb.Max) * 0.5
            if reg[0] <= c.X <= reg[2] and reg[1] <= c.Y <= reg[3]:
                host_ids.append(fi.Id)
        except Exception: pass
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: clear region'); _prep(t); t.Start()
    for i in host_ids + wall_ids:
        try: doc.Delete(i)
        except Exception: pass
    t.Commit()
result = {'walls': len(wall_ids), 'doors_windows': len(host_ids), 'deleted': not args.get('dry', True)}

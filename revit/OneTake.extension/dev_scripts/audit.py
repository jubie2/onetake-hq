# Full model audit -> plain text. args {"view":"Proposed Floor Plan","region":[x0,y0,x1,y1]}
from Autodesk.Revit.DB import (Dimension, View, ViewSchedule, Wall, BuiltInCategory, BuiltInParameter,
                               IndependentTag, SectionType, FamilyInstance)
vname = args.get('view', 'Proposed Floor Plan')
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == vname][0]
reg = args.get('region', [-8, -30, 72, 70])
def inreg(x, y): return reg[0] <= x <= reg[2] and reg[1] <= y <= reg[3]
L = []
L.append('DOC: %s' % doc.Title)
L.append('VIEW: %s (scale 1:%d)' % (view.Name, view.Scale))
# dimensions
L.append('--- DIMENSIONS in view')
ds = []
for d in FilteredElementCollector(doc, view.Id).OfClass(Dimension):
    bb = d.get_BoundingBox(view)
    if bb is None: continue
    cx, cy = (bb.Min.X + bb.Max.X) / 2.0, (bb.Min.Y + bb.Max.Y) / 2.0
    if not inreg(cx, cy): continue
    try: txt = d.ValueString
    except Exception: txt = '?'
    ds.append((cy, '  %-9s %-14s @(%.1f,%.1f)' % (d.Id.Value, txt, cx, cy)))
for _, s in sorted(ds, reverse=True): L.append(s)
L.append('  count: %d' % len(ds))
# walls
ws = [w for w in FilteredElementCollector(doc).OfClass(Wall)
      if w.Location and hasattr(w.Location, 'Curve') and inreg(w.Location.Curve.GetEndPoint(0).X, w.Location.Curve.GetEndPoint(0).Y)]
L.append('--- WALLS in region: %d' % len(ws))
# rooms
L.append('--- ROOMS (level 1, area>0)')
for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms):
    try:
        if r.Area <= 0: continue
        p = r.Location.Point
        if not inreg(p.X, p.Y): continue
        L.append('  %-9s %-42s %6.0f SF' % (r.Id.Value, r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(), r.Area))
    except Exception:
        pass
# equipment schedule
L.append('--- SCHEDULE')
for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
    if v.IsTemplate or v.Name != args.get('schedule', 'EQUIPMENT SCHEDULE (E) - PHO HUNG'): continue
    td = v.GetTableData(); sd = td.GetSectionData(SectionType.Body)
    items = []
    blanks = []
    for r in range(sd.NumberOfRows):
        row = [v.GetCellText(SectionType.Body, r, c) for c in range(sd.NumberOfColumns)]
        if row and row[0].strip():
            items.append(row[0].strip())
            miss = [i for i, cell in enumerate(row) if not cell.strip()]
            if miss: blanks.append('%s:%s' % (row[0].strip(), ','.join(str(m) for m in miss)))
    L.append('  view %s  items: %d  -> %s' % (v.Id.Value, len(items), ' '.join(items)))
    L.append('  empty cells by item (col idx): %s' % ('; '.join(blanks) if blanks else 'none'))
# tags
L.append('--- TAGS in view')
byhost = {}
for tg in FilteredElementCollector(doc, view.Id).OfClass(IndependentTag):
    try:
        for r in tg.GetTaggedReferences():
            byhost.setdefault(r.ElementId.Value, []).append(tg.TagText)
    except Exception:
        pass
L.append('  tagged elements: %d' % len(byhost))
# equipment instances carrying Item param
items = {}
for cat in (BuiltInCategory.OST_SpecialityEquipment, BuiltInCategory.OST_PlumbingFixtures,
            BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Casework,
            BuiltInCategory.OST_MechanicalEquipment, BuiltInCategory.OST_GenericModel):
    for e in FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType():
        p = e.LookupParameter('Item')
        if p is None or not p.AsString(): continue
        try:
            bb = e.get_BoundingBox(None)
            if bb is None or not inreg((bb.Min.X+bb.Max.X)/2, (bb.Min.Y+bb.Max.Y)/2): continue
        except Exception:
            continue
        items.setdefault(p.AsString().strip(), []).append(e.Id.Value)
L.append('--- ITEM instances: %d numbers' % len(items))
untagged = []
for k in sorted(items):
    for eid in items[k]:
        if eid not in byhost:
            untagged.append('%s:%s' % (k, eid))
L.append('  numbers: %s' % ' '.join('%s(%d)' % (k, len(items[k])) for k in sorted(items)))
L.append('  UNTAGGED: %s' % (' '.join(untagged) if untagged else 'none'))
result = '\n'.join(L)

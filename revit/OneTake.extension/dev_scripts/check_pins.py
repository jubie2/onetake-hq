# Check pinned / group state of ADU electrical fixtures; unpin if args.fix.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC, XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
fix = args.get('fix', False)
L = []
pinned = []
grouped = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(None)
        if b is None: continue
        c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, 0)
        if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
        gid = e.GroupId
        ing = gid is not None and gid != ElementId.InvalidElementId
        if ing: grouped += 1
        if e.Pinned:
            pinned.append(e)
    except Exception: pass
L.append('ADU electrical fixtures: %d pinned, %d in groups' % (len(pinned), grouped))
if fix and pinned:
    t = Transaction(doc, 'OneTake: unpin fixtures'); _prep(t); t.Start()
    for e in pinned:
        try: e.Pinned = False
        except Exception: pass
    t.Commit()
    L.append('unpinned %d' % len(pinned))
result = '\n'.join(L)

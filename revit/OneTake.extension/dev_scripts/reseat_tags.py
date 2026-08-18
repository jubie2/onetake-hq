# move every IndependentTag in the view whose host is in args.ids to host-bbox-center + (0, dy)
from Autodesk.Revit.DB import IndependentTag, View
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == args.get('view', 'Proposed Floor Plan')][0]
want = set(long(i) for i in args.get('ids', []))
dy = float(args.get('dy', 0.9))
moved = 0
t = Transaction(doc, 'OneTake: reseat tags'); _prep(t); t.Start()
for tg in FilteredElementCollector(doc, view.Id).OfClass(IndependentTag):
    try:
        hosts = [r.ElementId.Value for r in tg.GetTaggedReferences()]
    except Exception:
        continue
    if not hosts or hosts[0] not in want:
        continue
    el = doc.GetElement(ElementId(hosts[0]))
    bb = el.get_BoundingBox(None)
    if bb is None:
        continue
    c = (bb.Min + bb.Max) * 0.5
    tg.TagHeadPosition = XYZ(c.X, c.Y + dy, tg.TagHeadPosition.Z)
    moved += 1
t.Commit()
result = {'moved': moved}

# Label rooms in section/elevation views with text notes placed on the view plane.
# args {"views":[...], "clear":true, "dry":true}
from Autodesk.Revit.DB import (View, FilteredElementCollector as FEC, BuiltInCategory, BuiltInParameter,
                               TextNote, ElementTypeGroup, XYZ as _XYZ, ElementId as EId)
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: room labels'); _prep(t); t.Start()
for nm in args['views']:
    vs = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
    if not vs:
        L.append('%s: not found' % nm); continue
    v = vs[0]
    tf = v.CropBox.Transform; inv = tf.Inverse
    if args.get('clear') and not args.get('dry', True):
        for rt in list(FEC(doc, v.Id).OfCategory(BuiltInCategory.OST_RoomTags)):
            try: doc.Delete(rt.Id)
            except Exception: pass
    tnt = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
    n = 0; errs = []
    seen = set()
    for r in FEC(doc, v.Id).OfCategory(BuiltInCategory.OST_Rooms):
        try:
            label = r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() or ''
            bb = r.get_BoundingBox(v)
            if bb is None or not label: continue
            c = (bb.Min + bb.Max) * 0.5
            loc = inv.OfPoint(c)
            key = (label, round(loc.X, 1), round(loc.Y, 1))
            if key in seen: continue
            seen.add(key)
            pt = tf.OfPoint(_XYZ(loc.X, loc.Y, 0.0))
            if not args.get('dry', True):
                TextNote.Create(doc, v.Id, pt, label, tnt)
                doc.Regenerate()
            n += 1
        except Exception as ex:
            errs.append(str(ex)[:50])
    L.append('%-22s labels=%d %s' % (nm[:22], n, ('errs: ' + errs[0]) if errs else ''))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)

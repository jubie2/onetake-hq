# Rebuild keynote tags in the ADU sections using the office's 'Keynote Text arrow' tag.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag, Reference,
                               TagOrientation, BuiltInCategory as BIC, BuiltInParameter as BIP,
                               FamilySymbol, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
VIEWS = ['ADU - Section 1', 'ADU - Section 2', 'ADU - Section 3', 'ADU - Section 4']
L = []
tag = None
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_KeynoteTags): continue
        if (s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'Keynote Text arrow':
            tag = s; break
    except Exception: pass
L.append('tag type: %s' % (tag.Id if tag else 'NOT FOUND'))
# which categories to tag, and where to hang the tag relative to the element
WANT = ('Roofs', 'Walls', 'Floors', 'Ceilings')
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: L.append('%s missing' % nm); continue
    old = [t2.Id for t2 in FEC(doc, v.Id).OfClass(IndependentTag)]
    picks = []
    seenkey = set()
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else ''
            if cn not in WANT: continue
            b = e.get_BoundingBox(None)
            if b is None: continue
            cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
            if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
            t = doc.GetElement(e.GetTypeId())
            p = t.get_Parameter(BIP.KEYNOTE_PARAM) if t else None
            kv = p.AsString() if p else None
            if not kv: continue
            if kv in seenkey: continue
            seenkey.add(kv)
            picks.append((e, kv, cn))
        except Exception: pass
    L.append('%-18s existing tags %d -> tagging %d distinct keynotes %s' % (
        nm, len(old), len(picks), sorted(seenkey)))
    if not dry:
        t2 = Transaction(doc, 'OneTake: section keynotes'); _prep(t2); t2.Start()
        if not tag.IsActive: tag.Activate()
        if old: doc.Delete(List[ElementId](old))
        doc.Regenerate()
        bb = v.CropBox; tfm = bb.Transform; inv = tfm.Inverse
        i = 0
        for e, kv, cn in picks:
            b = e.get_BoundingBox(v)
            if b is None: continue
            # anchor on the element, place the bubble out to the right of the drawing
            ax = (b.Min.X + b.Max.X) / 2.0
            ay = (b.Min.Y + b.Max.Y) / 2.0
            az = (b.Min.Z + b.Max.Z) / 2.0
            q = inv.OfPoint(_XYZ(ax, ay, az))
            head = tfm.OfPoint(_XYZ(bb.Max.X - 3.0, q.Y, 0.0))
            try:
                IndependentTag.Create(doc, tag.Id, v.Id, Reference(e), True,
                                      TagOrientation.Horizontal, head)
                i += 1
            except Exception as ex:
                L.append('    fail %s %s' % (cn, str(ex)[:45]))
        doc.Regenerate(); t2.Commit()
        L.append('    placed %d' % i)
result = '\n'.join(L)

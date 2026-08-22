# Tag the ADU's doors and windows on the ADU floor plans. args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, FamilySymbol, View, IndependentTag,
                               Reference, TagOrientation, TagMode, XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
L = []
def tagsym(bic, fam):
    for s in FEC(doc).OfClass(FamilySymbol):
        try:
            if s.Category is None or s.Category.Id.IntegerValue != int(bic): continue
            if s.Family.Name == fam: return s
        except Exception: pass
    return None
DT = tagsym(BIC.OST_DoorTags, 'Door Tag')
WT = tagsym(BIC.OST_WindowTags, 'Window Tag')
L.append('door tag %s / window tag %s' % (DT.Id if DT else None, WT.Id if WT else None))
VIEWS = {}
for v in FEC(doc).OfClass(View):
    if v.IsTemplate: continue
    if v.Name == 'ADU - 1st Floor Plan': VIEWS['1st Floor Level'] = v
    if v.Name == 'ADU - 2nd Floor Plan': VIEWS['2nd FLoor Plan'] = v
jobs = []
for bic, sym in ((BIC.OST_Doors, DT), (BIC.OST_Windows, WT)):
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        b = e.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        lvn = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else ''
        v = VIEWS.get(lvn)
        if v is None: continue
        jobs.append((v, sym, e, _XYZ(cx, cy, 0)))
cnt = {}
for v, s, e, p in jobs:
    k = '%s / %s' % (v.Name[6:20], s.Category.Name)
    cnt[k] = cnt.get(k, 0) + 1
for k in sorted(cnt): L.append('  %-34s %d' % (k, cnt[k]))
if not dry:
    t = Transaction(doc, 'OneTake: ADU door/window tags'); _prep(t); t.Start()
    for s in (DT, WT):
        if s and not s.IsActive: s.Activate()
    doc.Regenerate()
    n = 0; fail = 0
    for v, s, e, p in jobs:
        try:
            IndependentTag.Create(doc, s.Id, v.Id, Reference(e), False,
                                  TagOrientation.Horizontal, p)
            n += 1
        except Exception as ex:
            fail += 1
            if fail < 3: L.append('  fail %s' % str(ex)[:60])
    doc.Regenerate(); t.Commit()
    L.append('placed %d tags, %d failed' % (n, fail))
result = '\n'.join(L)

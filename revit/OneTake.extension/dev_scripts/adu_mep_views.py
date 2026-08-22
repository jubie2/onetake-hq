# Split the ADU MEP plans into 1st + 2nd floor views. args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewPlan, ViewDuplicateOption,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, ElementId,
                               ImportInstance, BoundingBoxXYZ, XYZ as _XYZ)
from System.Collections.Generic import List
dry = args.get('dry', True)
L = []
byname = {}
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate: byname[v.Name] = v

RENAME = [('ADU - Electrical Plan', 'ADU - 1st Floor Electrical Plan'),
          ('ADU - Mechanical Plan', 'ADU - 1st Floor Mechanical Plan')]
NEW = [('2nd FLoor Electricall Plan', 'ADU - 2nd Floor Electrical Plan'),
       ('2nd FLoor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan')]
CATS = ['Sections', 'Elevations', 'Callouts', 'Reference Planes', 'Scope Boxes', 'Matchline']

for a, b in RENAME + NEW:
    L.append('%-32s -> %-34s src:%s dst-exists:%s' % (a, b, a in byname, b in byname))
if dry:
    result = '\n'.join(L)
else:
    t = Transaction(doc, 'OneTake: ADU MEP views'); _prep(t); t.Start()
    # 1. wipe the annotations I placed (they were stacked: both floors in one view)
    ev = byname.get('ADU - Electrical Plan') or byname.get('ADU - 1st Floor Electrical Plan')
    kill = []
    for e in FEC(doc, ev.Id).OfCategory(BIC.OST_GenericAnnotation):
        try:
            if e.Symbol.Family.Name in ('Smoke', 'High_efficacy_Light', "Fluor-vanity-light_2'"):
                kill.append(e.Id)
        except Exception: pass
    if kill:
        doc.Delete(List[ElementId](kill)); doc.Regenerate()
    L.append('removed %d stacked annotations' % len(kill))
    # 2. rename
    for a, b in RENAME:
        if a in byname and b not in byname:
            byname[a].Name = b; L.append('renamed %s -> %s' % (a, b))
    doc.Regenerate()
    # 3. duplicate the 2nd-floor source views and crop to the ADU
    ref = None
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == 'ADU - 2nd Floor Plan': ref = v; break
    rb = ref.CropBox
    cats = doc.Settings.Categories
    for src_n, new_n in NEW:
        exists = [v for v in FEC(doc).OfClass(View) if not v.IsTemplate and v.Name == new_n]
        if exists:
            L.append('%s already exists' % new_n); continue
        src = None
        for v in FEC(doc).OfClass(View):
            if not v.IsTemplate and v.Name == src_n: src = v; break
        if src is None:
            L.append('%s NOT FOUND' % src_n); continue
        nid = src.Duplicate(ViewDuplicateOption.WithDetailing)
        nv = doc.GetElement(nid)
        nv.Name = new_n
        nv.Scale = 48
        nb = BoundingBoxXYZ(); nb.Transform = nv.CropBox.Transform
        # map the reference crop through world into this view's local frame
        inv = nb.Transform.Inverse; rtf = rb.Transform
        xs = []; ys = []
        for x in (rb.Min.X, rb.Max.X):
            for y in (rb.Min.Y, rb.Max.Y):
                p = inv.OfPoint(rtf.OfPoint(_XYZ(x, y, 0.0)))
                xs.append(p.X); ys.append(p.Y)
        nb.Min = _XYZ(min(xs), min(ys), nv.CropBox.Min.Z)
        nb.Max = _XYZ(max(xs), max(ys), nv.CropBox.Max.Z)
        nv.CropBoxActive = True
        nv.CropBox = nb
        nv.CropBoxVisible = False
        p = nv.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
        if p and not p.IsReadOnly: p.Set(1)
        for cn in CATS:
            try:
                c = cats.get_Item(cn)
                if c is not None and nv.CanCategoryBeHidden(c.Id): nv.SetCategoryHidden(c.Id, True)
            except Exception: pass
        ids = [e.Id for e in FEC(doc, nv.Id).OfClass(ImportInstance)
               if e.CanBeHidden(nv) and not e.IsHidden(nv)]
        if ids: nv.HideElements(List[ElementId](ids))
        doc.Regenerate()
        L.append('created %s (%s) crop %.1f x %.1f' % (
            new_n, nv.Id, nb.Max.X - nb.Min.X, nb.Max.Y - nb.Min.Y))
    doc.Regenerate(); t.Commit()
    result = '\n'.join(L)

# Create ADU - Section 4 from scratch: transverse cut at X=1168, matching Section 1's setup.
# args {"x":1168.0,"flip":false,"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSection, ViewSheet, View,
                               BoundingBoxXYZ, Transform, XYZ as _XYZ, ElementId,
                               BuiltInParameter as BIP, ImportInstance, ViewFamilyType)
from System.Collections.Generic import List
CX = float(args.get('x', 1168.0))
flip = args.get('flip', False)
dry = args.get('dry', True)
NAME = 'ADU - Section 4'
CATS = ['Sections', 'Elevations', 'Callouts', 'Reference Planes', 'Scope Boxes', 'Matchline']
L = []
old = [v for v in FEC(doc).OfClass(ViewSection) if not v.IsTemplate and v.Name == NAME]
L.append('existing %s' % [str(v.Id) for v in old])
if not dry:
    t = Transaction(doc, 'OneTake: ADU Section 4'); _prep(t); t.Start()
    if old:
        for v in old:
            for s in FEC(doc).OfClass(ViewSheet):
                pass
        doc.Delete(List[ElementId]([v.Id for v in old])); doc.Regenerate()
        L.append('deleted previous')
    st = None
    for ft in FEC(doc).OfClass(ViewFamilyType):
        if str(ft.ViewFamily) == 'Section' and \
           (ft.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'Building Section':
            st = ft; break
    right = _XYZ(0, -1, 0) if flip else _XYZ(0, 1, 0)
    up = _XYZ(0, 0, 1)
    tf = Transform.Identity
    tf.Origin = _XYZ(CX, -138.0, 13.5)
    tf.BasisX = right
    tf.BasisY = up
    tf.BasisZ = right.CrossProduct(up)
    bb = BoundingBoxXYZ()
    bb.Transform = tf
    bb.Min = _XYZ(-22.0, -17.5, 0.0)
    bb.Max = _XYZ(22.0, 17.5, 30.0)
    nv = ViewSection.CreateSection(doc, st.Id, bb)
    nv.Name = NAME
    nv.Scale = 48
    p = nv.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
    if p and not p.IsReadOnly: p.Set(1)
    cats = doc.Settings.Categories
    for cn in CATS:
        try:
            c = cats.get_Item(cn)
            if c is not None and nv.CanCategoryBeHidden(c.Id): nv.SetCategoryHidden(c.Id, True)
        except Exception: pass
    doc.Regenerate()
    ids = [e.Id for e in FEC(doc, nv.Id).OfClass(ImportInstance)
           if e.CanBeHidden(nv) and not e.IsHidden(nv)]
    if ids: nv.HideElements(List[ElementId](ids))
    doc.Regenerate()
    d = nv.ViewDirection; o = nv.Origin
    cb = nv.CropBox
    L.append('created %s  origin (%.1f,%.1f,%.1f) dir (%.2f,%.2f,%.2f)' % (
        nv.Id, o.X, o.Y, o.Z, d.X, d.Y, d.Z))
    L.append('crop local %.1f..%.1f x %.1f..%.1f' % (cb.Min.X, cb.Max.X, cb.Min.Y, cb.Max.Y))
    t.Commit()
result = '\n'.join(L)

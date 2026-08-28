# Hide parcel DXF + cameras in new mech/elec views; give their viewports the
# titled viewport type (copied from the 2nd-floor viewport on each sheet).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: stray fix'); _prep(t); t.Start()
dxf = doc.GetElement(ElementId(2185245))
cam = doc.GetElement(ElementId(134722))
for vid in [2244930, 2244950]:
    v = doc.GetElement(ElementId(vid))
    for e in [dxf, cam]:
        try:
            v.HideElements(__import__('System.Collections.Generic', fromlist=['List']).List[ElementId]([e.Id]))
        except Exception:
            try:
                cat = e.Category
                v.SetCategoryHidden(cat.Id, True)
                L.append('%s: hid category %s' % (vid, cat.Name))
                continue
            except Exception as ex:
                L.append('%s: fail %s' % (vid, str(ex)[:40]))
        L.append('%s: hid element %s' % (vid, e.Id.Value))
doc.Regenerate()
for sn, vid, refname in [('A200', 2244930, 'ADU 2nd Floor Mech Plan'),
                         ('A201', 2244950, 'ADU 2nd Floor Elec Plan')]:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber != sn: continue
        reftype = None
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if doc.GetElement(vp.ViewId).Name == refname:
                reftype = vp.GetTypeId()
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if vp.ViewId.Value == vid and reftype is not None:
                try:
                    vp.ChangeTypeId(reftype)
                    vp.LabelOffset = _XYZ(0.06, -0.05, 0)
                    L.append('%s vp type set' % sn)
                except Exception as ex:
                    L.append('%s type %s' % (sn, str(ex)[:40]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

# Put the re-cut views back on A103 (sections) and A105 (elevations).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, BuiltInParameter as BIP)
from System.Collections.Generic import List
PLACE = {
 'A105': [(2245112, 0.62, 1.42), (2245103, 1.85, 1.42),
          (2245130, 0.62, 0.42), (2245121, 1.85, 0.42)],
 'A103': [(2245139, 0.62, 1.42), (2245148, 1.85, 1.42),
          (2245157, 0.62, 0.42), (2245166, 1.85, 0.42)],
}
L = []
t = Transaction(doc, 'OneTake: place re-cut views'); _prep(t); t.Start()
for sn, items in PLACE.items():
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn: sh = s
    if sh is None: L.append('%s missing' % sn); continue
    reftype = None
    dead = []
    for vp in FEC(doc, sh.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        if reftype is None and v.ViewType.ToString() in ('Section', 'Elevation'):
            reftype = vp.GetTypeId()
        if v is None or v.Id.Value in [i[0] for i in items]:
            dead.append(vp.Id)
    if dead: doc.Delete(List[ElementId](dead))
    doc.Regenerate()
    for vid, cx, cy in items:
        v = doc.GetElement(ElementId(vid))
        p = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
        if p and not p.IsReadOnly: p.Set(1)
        vp = Viewport.Create(doc, sh.Id, ElementId(vid), _XYZ(cx, cy, 0))
        doc.Regenerate()
        if reftype is not None:
            try: vp.ChangeTypeId(reftype)
            except Exception: pass
        try: vp.LabelOffset = _XYZ(0.06, -0.05, 0)
        except Exception: pass
        ol = vp.GetBoxOutline()
        L.append('%s %-16s box (%.2f,%.2f)-(%.2f,%.2f)' % (
            sn, v.Name, ol.MinimumPoint.X, ol.MinimumPoint.Y,
            ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

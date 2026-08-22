# Report/repair level visibility in a view. args {"view":"West Elev.","unhide":false}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, Level, ElementId,
                               DatumExtentType, DatumEnds, Line, XYZ as _XYZ)
from System.Collections.Generic import List
name = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == name: v = x; break
L = ['view %s' % name]
lv = list(FEC(doc).OfClass(Level))
for l in lv:
    L.append('  %-20s id %s hidden=%s' % (l.Name[:20], l.Id, l.IsHidden(v)))
if args.get('unhide'):
    ids = List[ElementId]([l.Id for l in lv if l.IsHidden(v)])
    if ids.Count:
        t = Transaction(doc, 'OneTake: unhide levels'); _prep(t); t.Start()
        v.UnhideElements(ids)
        bb = v.CropBox; pad = 1.5
        for l in lv:
            try:
                for e in (DatumEnds.End0, DatumEnds.End1):
                    l.SetDatumExtentType(e, v, DatumExtentType.ViewSpecific)
                cs = l.GetCurvesInView(DatumExtentType.ViewSpecific, v)
                for c in cs:
                    p0 = c.GetEndPoint(0)
                    ln = Line.CreateBound(_XYZ(bb.Min.X - pad, p0.Y, p0.Z),
                                          _XYZ(bb.Max.X + pad, p0.Y, p0.Z))
                    l.SetCurveInView(DatumExtentType.ViewSpecific, v, ln)
            except Exception as ex:
                L.append('  trim %s: %s' % (l.Name[:18], str(ex)[:60]))
        doc.Regenerate(); t.Commit()
        L.append('  unhid %s levels' % ids.Count)
result = '\n'.join(L)

# Report the views on a sheet + their crop in world coords. args {"sheet":"A105"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               BuiltInCategory as BIC, XYZ as _XYZ)
L = []
sn = args.get('sheet', 'A105')
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == sn: sh = s; break
if sh is None:
    result = 'sheet %s not found' % sn
else:
    L.append('SHEET %s  %s' % (sh.SheetNumber, sh.Name))
    for vpid in sh.GetAllViewports():
        vp = doc.GetElement(vpid)
        v = doc.GetElement(vp.ViewId)
        bb = v.CropBox; tf = bb.Transform
        # world corners of the crop rectangle
        pts = []
        for x in (bb.Min.X, bb.Max.X):
            for y in (bb.Min.Y, bb.Max.Y):
                p = tf.OfPoint(_XYZ(x, y, 0.0)); pts.append(p)
        xs = [p.X for p in pts]; ys = [p.Y for p in pts]; zs = [p.Z for p in pts]
        d = v.ViewDirection
        L.append('%s | id %s | scale %s | cropOn %s' % (v.Name, v.Id, v.Scale, v.CropBoxActive))
        L.append('   local crop %.2f..%.2f x %.2f..%.2f  (%.1f x %.1f ft)' % (
            bb.Min.X, bb.Max.X, bb.Min.Y, bb.Max.Y, bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y))
        L.append('   world  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  dir(%.2f,%.2f,%.2f)' % (
            min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), d.X, d.Y, d.Z))
        ol = vp.GetBoxOutline()
        L.append('   viewport box %.2f x %.2f at (%.2f,%.2f)' % (
            ol.MaximumPoint.X-ol.MinimumPoint.X, ol.MaximumPoint.Y-ol.MinimumPoint.Y,
            vp.GetBoxCenter().X, vp.GetBoxCenter().Y))
result = '\n'.join(L)

from Autodesk.Revit.DB import View, Viewport, ViewSheet, BuiltInParameter
name = args.get('view', 'ADU - North Elevation')
L = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate or v.Name != name: continue
    bb = v.CropBox
    L.append('view %s  id=%s  type=%s' % (v.Name, v.Id.Value, v.ViewType))
    L.append('  Scale=%s  DetailLevel=%s  cropActive=%s' % (v.Scale, v.DetailLevel, v.CropBoxActive))
    L.append('  CropBox local  X %.2f..%.2f (%.1f ft)   Y %.2f..%.2f (%.1f ft)  Z %.1f..%.1f' %
             (bb.Min.X, bb.Max.X, bb.Max.X-bb.Min.X, bb.Min.Y, bb.Max.Y, bb.Max.Y-bb.Min.Y, bb.Min.Z, bb.Max.Z))
    p = v.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE)
    L.append('  annotation crop = %s' % (p.AsInteger() if p else 'n/a'))
    try:
        mgr = v.GetCropRegionShapeManager()
        L.append('  anno offsets  L%.2f R%.2f T%.2f B%.2f' %
                 (mgr.LeftAnnotationCropOffset, mgr.RightAnnotationCropOffset,
                  mgr.TopAnnotationCropOffset, mgr.BottomAnnotationCropOffset))
    except Exception as ex:
        L.append('  shape mgr: %s' % ex)
    for vp in FilteredElementCollector(doc).OfClass(Viewport):
        if vp.ViewId != v.Id: continue
        o = vp.GetBoxOutline(); lo = vp.GetLabelOutline()
        sh = doc.GetElement(vp.SheetId)
        L.append('  viewport on %s: box %.2f x %.2f   label %.2f x %.2f' %
                 (sh.SheetNumber, o.MaximumPoint.X-o.MinimumPoint.X, o.MaximumPoint.Y-o.MinimumPoint.Y,
                  lo.MaximumPoint.X-lo.MinimumPoint.X, lo.MaximumPoint.Y-lo.MinimumPoint.Y))
result = '\n'.join(L)

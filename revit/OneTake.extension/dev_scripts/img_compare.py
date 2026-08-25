from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ImageInstance,
                               StorageType)
L = []
for sn in ('A01', 'A04'):
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn: sh = s; break
    for e in FEC(doc, sh.Id).OfClass(ImageInstance):
        L.append('=== %s image %s ownerView=%s' % (sn, e.Id, e.OwnerViewId))
        try:
            loc = e.Location
            L.append('   Location type: %s' % type(loc).__name__)
        except Exception: pass
        b = e.get_BoundingBox(sh)
        L.append('   bbox (%.3f,%.3f)-(%.3f,%.3f)' % (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y))
        for p in e.Parameters:
            try:
                if p.StorageType == StorageType.String: v = p.AsString()
                elif p.StorageType == StorageType.Integer: v = p.AsInteger()
                elif p.StorageType == StorageType.Double: v = round(p.AsDouble(), 4)
                else: v = p.AsValueString()
                if v in (None, ''): continue
                L.append('   %-24s = %r' % (p.Definition.Name, v))
            except Exception: pass
result = '\n'.join(L)

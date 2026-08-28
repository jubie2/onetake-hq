# Audit: ProjectInformation + which world region each sheet's model views look at.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ViewType, XYZ as _XYZ)
L = []
pi = doc.ProjectInformation
for pn in ['Project Name', 'Project Address', 'Project Number', 'Client Name',
           'Project Status', 'Project Issue Date']:
    p = pi.LookupParameter(pn)
    L.append('PI %s = %r' % (pn, p.AsString() if p else None))
SHEETS = ['A02', 'A103', 'A104', 'A105', 'A200', 'A201', 'S', 'S101', 'AD1',
          'A06', 'L1', 'A102']
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber not in SHEETS: continue
    L.append('--- %s %s ---' % (s.SheetNumber, s.Name))
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        c = vp.GetBoxCenter()
        info = ''
        try:
            if v.ViewType in (ViewType.Section, ViewType.Elevation):
                o = v.Origin; d = v.ViewDirection
                info = 'origin (%.0f,%.0f,%.0f) dir (%.1f,%.1f,%.1f)' % (
                    o.X, o.Y, o.Z, d.X, d.Y, d.Z)
            else:
                cb = v.CropBox; T = cb.Transform
                a = T.OfPoint(_XYZ(cb.Min.X, cb.Min.Y, 0))
                b = T.OfPoint(_XYZ(cb.Max.X, cb.Max.Y, 0))
                info = 'world (%.0f,%.0f)-(%.0f,%.0f)' % (
                    min(a.X, b.X), min(a.Y, b.Y), max(a.X, b.X), max(a.Y, b.Y))
        except Exception as ex:
            info = str(ex)[:40]
        L.append('  [%s] %s | vp(%.2f,%.2f) | %s' % (v.ViewType, v.Name, c.X, c.Y, info))
result = '\n'.join(L)

# A02 fixes: rewrite plumbing calc for Electric Ave duplex ADU, delete empty cloud,
# tighten Site crop + reposition title, find signature curves; also rename project
# to Duplex ADU on A01 texts + ProjectInformation.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, BoundingBoxXYZ, CurveElement,
                               FilledRegion)
L = []
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A02': sh = s
# find signature-area curves/regions BEFORE transaction (collection gotcha)
sig = []
for e in FEC(doc, sh.Id).OfClass(CurveElement):
    bb = e.get_BoundingBox(sh)
    if bb and 1.5 < bb.Min.X < 2.1 and 0.05 < bb.Min.Y < 0.16 and (bb.Max.X - bb.Min.X) < 0.5:
        sig.append(e.Id)
for e in FEC(doc, sh.Id).OfClass(FilledRegion):
    bb = e.get_BoundingBox(sh)
    if bb and 1.5 < bb.Min.X < 2.1 and 0.05 < bb.Min.Y < 0.16:
        sig.append(e.Id)
L.append('signature candidates: %s' % [i.Value for i in sig])
t = Transaction(doc, 'OneTake: A02 content'); _prep(t); t.Start()
# 1. plumbing calc
e = doc.GetElement(ElementId(2148238))
e.Text = ('TOTAL PLUMBING FIXTURE CALCULATION\r\r'
          'EXISTING RESIDENCE (2-STORY):\r'
          '\tEXISTING PLUMBING FIXTURES TO REMAIN\r'
          '\t(NO CHANGE)')
e = doc.GetElement(ElementId(2148246))
e.Text = ('\rNEW DUPLEX ADU:\r\r'
          '\tUNIT 1 (1ST FLOOR):\t(2) Lavatory\r'
          '\t\t\t(1) Kitchen Sink\r'
          '\t\t\t(1) Bathtub\r'
          '\t\t\t(1) Shower\r'
          '\t\t\t(2) Water Closet\r'
          '\t\t\t(1) Clothes Washer\r'
          '\t\t\t(1) Dishwasher\r\r'
          '\tUNIT 2 (2ND FLOOR):\t(2) Lavatory\r'
          '\t\t\t(1) Kitchen Sink\r'
          '\t\t\t(1) Bathtub\r'
          '\t\t\t(1) Shower\r'
          '\t\t\t(2) Water Closet\r'
          '\t\t\t(1) Clothes Washer\r'
          '\t\t\t(1) Dishwasher')
L.append('plumbing calc rewritten')
# 2. delete empty cloud
try:
    doc.Delete(ElementId(2148200)); L.append('cloud 2148200 deleted')
except Exception as ex:
    L.append('cloud del fail %s' % str(ex)[:40])
# 3. tighten Site crop + reposition
v = None
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    vv = doc.GetElement(vp.ViewId)
    if vv.Name == 'Site': v = vv; svp = vp
cb = v.CropBox; T = cb.Transform; inv = T.Inverse
lo = inv.OfPoint(_XYZ(1085, 25, T.Origin.Z))
hi = inv.OfPoint(_XYZ(1235, 128, T.Origin.Z))
nb = BoundingBoxXYZ(); nb.Transform = T
nb.Min = _XYZ(min(lo.X, hi.X), min(lo.Y, hi.Y), cb.Min.Z)
nb.Max = _XYZ(max(lo.X, hi.X), max(lo.Y, hi.Y), cb.Max.Z)
v.CropBox = nb
doc.Regenerate()
svp.SetBoxCenter(_XYZ(0.80, 1.35, 0))
doc.Regenerate()
ol = svp.GetBoxOutline()
try: svp.LabelOffset = _XYZ(0.30, -0.03, 0)
except Exception: pass
L.append('Site box now (%.2f,%.2f)-(%.2f,%.2f)' % (
    ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

# Re-cut on the TRUE building footprint (from opening stations, not the wall sweep
# which caught neighbouring site walls), and lay both sheets out with the keynote
# legend in the clear band between the two rows of drawings.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewFamilyType,
                               ViewFamily, ViewSection, ViewSheet, Viewport, ViewType,
                               BoundingBoxXYZ, Transform, ElementId, XYZ as _XYZ,
                               Category, BuiltInCategory as BIC, BuiltInParameter as BIP)
from System.Collections.Generic import List
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
# true footprint centre: s in [-31,+27], t in [-7,+20.5]  (was (0,0) of the old frame)
BX, BY = 1161.1251, 98.8210
CX = BX + UX * (-2.0) + VX * 6.75
CY = BY + UY * (-2.0) + VY * 6.75
HS, HT = 29.0, 13.75
def W(s, t):
    return (CX + UX * s + VX * t, CY + UY * s + VY * t)
U = _XYZ(UX, UY, 0); V = _XYZ(VX, VY, 0)
nU = _XYZ(-UX, -UY, 0); nV = _XYZ(-VX, -VY, 0)
JOBS = [
 ('ADU North Elev', 'North Elev.', U,  (0.0,  HT + 6.0), 33.0, 2 * HT + 12.0),
 ('ADU South Elev', 'South Elev.', nU, (0.0, -HT - 6.0), 33.0, 2 * HT + 12.0),
 ('ADU East Elev',  'East Elev.',  nV, ( HS + 6.0, 0.0), 20.0, 2 * HS + 12.0),
 ('ADU West Elev',  'West Elev.',  V,  (-HS - 6.0, 0.0), 20.0, 2 * HS + 12.0),
 ('ADU Section 1',  'Section 1',   V,  (-20.0, 0.0), 20.0, 55.0),
 ('ADU Section 2',  'Section 2',   nV, ( 18.0, 0.0), 20.0, 55.0),
 ('ADU Section 3',  'Section 3',   U,  (0.0,  11.0), 33.0, 26.0),
 ('ADU Section 4',  'Section 4',   nU, (0.0,  -3.0), 33.0, 32.0),
]
OLD = [2245103, 2245112, 2245121, 2245130, 2245139, 2245148, 2245157, 2245166]
vft = None
for x in FEC(doc).OfClass(ViewFamilyType):
    if x.ViewFamily == ViewFamily.Section: vft = x; break
seccat = Category.GetCategory(doc, BIC.OST_Sections)
elevcat = Category.GetCategory(doc, BIC.OST_Elev)
L = ['centre world (%.3f,%.3f)' % (CX, CY)]
t = Transaction(doc, 'OneTake: re-cut on true footprint'); _prep(t); t.Start()
kill = List[ElementId]()
for vid in OLD:
    if doc.GetElement(ElementId(vid)) is not None: kill.Add(ElementId(vid))
if kill.Count: doc.Delete(kill); L.append('deleted %d views' % kill.Count)
doc.Regenerate()
made = {}
for name, title, bx, (os_, ot), hw, depth in JOBS:
    ox, oy = W(os_, ot)
    tf = Transform.Identity
    tf.Origin = _XYZ(ox, oy, 0)
    tf.BasisX = bx
    tf.BasisY = _XYZ(0, 0, 1)
    tf.BasisZ = bx.CrossProduct(_XYZ(0, 0, 1))
    bb = BoundingBoxXYZ()
    bb.Transform = tf
    bb.Min = _XYZ(-hw, -4.0, 0)
    bb.Max = _XYZ(hw, 32.0, depth)
    v = ViewSection.CreateSection(doc, vft.Id, bb)
    v.Name = name
    v.Scale = 64
    p = v.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    for c in (seccat, elevcat):
        try: v.SetCategoryHidden(c.Id, True)
        except Exception: pass
    p2 = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
    if p2 and not p2.IsReadOnly: p2.Set(1)
    made[name] = (v.Id, ox, oy, hw)
    L.append('%-16s id %-9s origin (%.2f,%.2f) hw %.1f' % (name, v.Id.Value, ox, oy, hw))
doc.Regenerate()
LAYOUT = {
 'A105': [('ADU South Elev', 0.62, 1.55), ('ADU North Elev', 1.85, 1.55),
          ('ADU West Elev', 0.62, 0.40),  ('ADU East Elev', 1.85, 0.40)],
 'A103': [('ADU Section 1', 0.62, 1.55), ('ADU Section 2', 1.85, 1.55),
          ('ADU Section 3', 0.62, 0.40), ('ADU Section 4', 1.85, 0.40)],
}
for sn, items in LAYOUT.items():
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn: sh = s
    reftype = None
    for vp in FEC(doc, sh.Id).OfClass(Viewport):
        v2 = doc.GetElement(vp.ViewId)
        if v2 is not None and v2.ViewType == ViewType.Section:
            reftype = vp.GetTypeId()
    for nm, cx, cy in items:
        vid = made[nm][0]
        vp = Viewport.Create(doc, sh.Id, vid, _XYZ(cx, cy, 0))
        doc.Regenerate()
        if reftype is not None:
            try: vp.ChangeTypeId(reftype)
            except Exception: pass
        try: vp.LabelOffset = _XYZ(0.06, -0.05, 0)
        except Exception: pass
        ol = vp.GetBoxOutline()
        L.append('%s %-16s box (%.2f,%.2f)-(%.2f,%.2f)' % (
            sn, nm, ol.MinimumPoint.X, ol.MinimumPoint.Y,
            ol.MaximumPoint.X, ol.MaximumPoint.Y))
    # keynote legend into the clear band between the rows
    for vp in FEC(doc, sh.Id).OfClass(Viewport):
        v2 = doc.GetElement(vp.ViewId)
        if v2 is not None and v2.ViewType == ViewType.Legend:
            vp.SetBoxCenter(_XYZ(1.24, 0.95, 0))
            doc.Regenerate()
            ol = vp.GetBoxOutline()
            L.append('%s legend "%s" -> (%.2f,%.2f)-(%.2f,%.2f)' % (
                sn, v2.Name, ol.MinimumPoint.X, ol.MinimumPoint.Y,
                ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

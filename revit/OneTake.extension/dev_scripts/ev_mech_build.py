# Build ADU mechanical plans: duplicate floor plans, crop, room-tag, keynote-tag,
# and swap onto A200 (removing old Logan mech vps + attic section).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ViewDuplicateOption, ElementId, XYZ as _XYZ, UV,
                               BoundingBoxXYZ, LinkElementId, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from System.Collections.Generic import List
L = []
def crop_to(v, x0, y0, x1, y1):
    cb = v.CropBox; T = cb.Transform; inv = T.Inverse
    pts = [inv.OfPoint(_XYZ(x, y, T.Origin.Z)) for (x, y) in
           [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    nb = BoundingBoxXYZ(); nb.Transform = T
    nb.Min = _XYZ(min(p.X for p in pts), min(p.Y for p in pts), cb.Min.Z)
    nb.Max = _XYZ(max(p.X for p in pts), max(p.Y for p in pts), cb.Max.Z)
    v.CropBox = nb
TAGS1 = [  # 1st floor: (n, ex, ey, dx, dy)
 ('1', 1146.0, 101.0, 3, -3), ('2', 1148.6, 102.3, 4, 2), ('2', 1135.3, 106.7, -4, 2),
 ('2', 1137.8, 91.3, -4, -2), ('3', 1152.0, 124.5, 3, 2), ('4', 1141.8, 108.9, -3, 3),
 ('4', 1146.7, 94.6, 3, -3), ('5', 1170.0, 119.3, -2, -4), ('6', 1170.0, 122.6, 2, 3),
 ('7', 1160.5, 113.8, 3, -3), ('8', 1161.0, 116.5, 3, 1), ('9', 1161.0, 122.6, -2, 3),
 ('10', 1174.0, 119.5, 2, -3), ('11', 1174.3, 119.8, 3, 1), ('12', 1137.0, 103.8, -5, -1),
 ('12', 1138.5, 93.5, -2, 4), ('12', 1143.0, 100.5, 2, -5), ('13', 1144.5, 101.5, 4, -4),
 ('14', 1151.5, 104.5, 2, 4),
]
TAGS2 = [  # 2nd floor
 ('1', 1150.0, 101.0, 2, -4), ('2', 1159.7, 102.7, 4, -2), ('2', 1138.1, 107.4, -4, 2),
 ('2', 1140.6, 92.9, -4, -2), ('4', 1145.6, 111.0, -2, 4), ('4', 1147.7, 94.7, 2, -4),
 ('7', 1175.2, 111.8, -3, 2), ('8', 1176.0, 113.0, 3, 2), ('9', 1180.5, 115.5, 3, 3),
 ('5', 1169.8, 100.8, -3, -3), ('6', 1171.5, 96.0, 2, -3), ('10', 1181.0, 116.5, -2, 3),
 ('11', 1181.4, 116.9, 3, 1), ('12', 1139.5, 105.5, -3, -3), ('12', 1141.5, 94.5, -1, -4),
 ('12', 1147.0, 102.0, 0, 4), ('13', 1148.5, 103.0, 3, 3),
]
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200': sh = s
oldvp = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if v.Name in ('1st Floor Mechanical Plan', '2nd FLoor Mechanical Plan',
                  'ATTIC SECTION'): oldvp.append(vp.Id)
t = Transaction(doc, 'OneTake: ADU mech plans'); _prep(t); t.Start()
if not sym.IsActive: sym.Activate(); doc.Regenerate()
made = []
for srcid, name, title, tags, cx in [
        (718579, 'ADU 1st Floor Mech Plan', '1st Floor Mechanical Plan', TAGS1, 2.38),
        (1715860, 'ADU 2nd Floor Mech Plan', '2nd FLoor Mechanical Plan', TAGS2, 1.31)]:
    src = doc.GetElement(ElementId(srcid))
    nid = src.Duplicate(ViewDuplicateOption.Duplicate)
    nv = doc.GetElement(nid)
    nv.Name = name
    nv.Scale = 64
    p = nv.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    crop_to(nv, 1126, 82, 1194, 128)
    doc.Regenerate()
    # room tags
    nrt = 0
    for r in FEC(doc).OfCategory(BIC.OST_Rooms):
        try:
            rp = r.Location.Point
            if not (1126 < rp.X < 1194 and 82 < rp.Y < 128): continue
            if r.LevelId != nv.GenLevel.Id: continue
            doc.Create.NewRoomTag(LinkElementId(r.Id), UV(rp.X, rp.Y), nid)
            nrt += 1
        except Exception: pass
    # keynote tags
    nk = 0
    placed = []
    for (n, ex, ey, dx, dy) in tags:
        try:
            pt = _XYZ(ex + dx, ey + dy, 0)
            fi = doc.Create.NewFamilyInstance(pt, sym, nv)
            pp = fi.LookupParameter('TEXT')
            if pp: pp.Set(n)
            doc.Regenerate()
            e = doc.GetElement(fi.Id)
            try:
                e.addLeader(); doc.Regenerate()
                lds = list(e.GetLeaders())
                if lds:
                    lds[-1].End = _XYZ(ex, ey, 0)
                    try: lds[-1].Elbow = _XYZ(ex + dx * 0.45, ey + dy * 0.45, 0)
                    except Exception: pass
            except Exception: pass
            placed.append((fi.Id, n)); nk += 1
        except Exception as ex2:
            L.append('tag %s fail %s' % (n, str(ex2)[:40]))
    doc.Regenerate()
    for eid, n in placed:
        p2 = doc.GetElement(eid).LookupParameter('TEXT')
        if p2 and p2.AsString() != n: p2.Set(n)
    made.append((nid, cx))
    L.append('%s: %d room tags, %d keynotes' % (name, nrt, nk))
if oldvp: doc.Delete(List[ElementId](oldvp)); L.append('removed %d old vps' % len(oldvp))
doc.Regenerate()
for nid, cx in made:
    vp = Viewport.Create(doc, sh.Id, nid, _XYZ(cx, 1.45, 0))
    doc.Regenerate()
    try: vp.LabelOffset = _XYZ(0.06, -0.045, 0)
    except Exception: pass
    ol = vp.GetBoxOutline()
    L.append('vp box (%.2f,%.2f)-(%.2f,%.2f)' % (
        ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

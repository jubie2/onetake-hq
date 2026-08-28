# Repair dependent-view mess on the 1st floor:
# - remove shared mech TAG LABELs + duplicate room tags from the dependent family
# - rebuild independent mech/elec 1st-floor views from the primary view
# - re-place mech keynotes + room tags there; swap viewports on A200/A201
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, ViewDuplicateOption, ElementId, XYZ as _XYZ,
                               UV, LinkElementId, FamilySymbol, Category,
                               BoundingBoxXYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, PlanViewPlane)
from System.Collections.Generic import List
L = []
v718 = doc.GetElement(ElementId(718579))
prim = v718.GetPrimaryViewId()
L.append('primary of 718579 = %s' % prim.Value)
if prim == ElementId.InvalidElementId:
    prim = ElementId(718579)
pv = doc.GetElement(prim)
# collect shared TAG LABELs + roomtag dupes (before transaction)
tags = []
for e in FEC(doc, ElementId(718579)).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name == 'TAG LABEL': tags.append(e.Id)
    except Exception: pass
seen = {}
rtdel = []
for e in FEC(doc, ElementId(718579)).OfCategory(BIC.OST_RoomTags).WhereElementIsNotElementType():
    try:
        rid = e.Room.Id.Value
        if rid in seen: rtdel.append(e.Id)
        else: seen[rid] = e.Id
    except Exception: pass
oldviews = [ElementId(2244742), ElementId(2244891)]
oldvps = []
for sn in ['A200', 'A201']:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn:
            for vp in FEC(doc, s.Id).OfClass(Viewport):
                if vp.ViewId in oldviews: oldvps.append(vp.Id)
sym = None
for s2 in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s2.Family.Name == 'TAG LABEL': sym = s2; break
TAGS1 = [
 ('1', 1146.0, 101.0, 3, -3), ('2', 1148.6, 102.3, 4, 2), ('2', 1135.3, 106.7, -4, 2),
 ('2', 1137.8, 91.3, -4, -2), ('3', 1152.0, 124.5, 3, 2), ('4', 1141.8, 108.9, -3, 3),
 ('4', 1146.7, 94.6, 3, -3), ('5', 1170.0, 119.3, -2, -4), ('6', 1170.0, 122.6, 2, 3),
 ('7', 1160.5, 113.8, 3, -3), ('8', 1161.0, 116.5, 3, 1), ('9', 1161.0, 122.6, -2, 3),
 ('10', 1174.0, 119.5, 2, -3), ('11', 1174.3, 119.8, 3, 1), ('12', 1137.0, 103.8, -5, -1),
 ('12', 1138.5, 93.5, -2, 4), ('12', 1143.0, 100.5, 2, -5), ('13', 1144.5, 101.5, 4, -4),
 ('14', 1151.5, 104.5, 2, 4),
]
seccat = Category.GetCategory(doc, BIC.OST_Sections)
elevcat = Category.GetCategory(doc, BIC.OST_Elev)
ecat = Category.GetCategory(doc, BIC.OST_ElectricalFixtures)
lcat = Category.GetCategory(doc, BIC.OST_LightingFixtures)
t = Transaction(doc, 'OneTake: fix dependents'); _prep(t); t.Start()
if not sym.IsActive: sym.Activate(); doc.Regenerate()
if tags: doc.Delete(List[ElementId](tags)); L.append('deleted %d shared tags' % len(tags))
if rtdel: doc.Delete(List[ElementId](rtdel)); L.append('deleted %d dup roomtags' % len(rtdel))
if oldvps: doc.Delete(List[ElementId](oldvps))
for ov in oldviews:
    try: doc.Delete(ov)
    except Exception: pass
L.append('old dependent mech/elec views removed')
doc.Regenerate()
cb718 = v718.CropBox
made = {}
for key, name, title in [('mech', 'ADU 1st Floor Mech Plan', '1st Floor Mechanical Plan'),
                         ('elec', 'ADU 1st Floor Elec Plan', '1st Floor Electrical Plan')]:
    nid = pv.Duplicate(ViewDuplicateOption.Duplicate)
    nv = doc.GetElement(nid)
    nv.Name = name
    nv.Scale = 64
    p = nv.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    nb = BoundingBoxXYZ(); nb.Transform = cb718.Transform
    nb.Min = cb718.Min; nb.Max = cb718.Max
    nv.CropBox = nb
    nv.CropBoxActive = True
    for c in [seccat, elevcat]:
        try: nv.SetCategoryHidden(c.Id, True)
        except Exception: pass
    if key == 'mech':
        for c in [ecat, lcat]:
            try: nv.SetCategoryHidden(c.Id, True)
            except Exception: pass
    else:
        try:
            vr = nv.GetViewRange()
            vr.SetOffset(PlanViewPlane.TopClipPlane, 10.5)
            nv.SetViewRange(vr)
        except Exception: pass
    doc.Regenerate()
    nrt = 0
    for r in FEC(doc).OfCategory(BIC.OST_Rooms):
        try:
            rp = r.Location.Point
            if not (1126 < rp.X < 1194 and 82 < rp.Y < 128): continue
            if r.LevelId != nv.GenLevel.Id: continue
            doc.Create.NewRoomTag(LinkElementId(r.Id), UV(rp.X, rp.Y), nid)
            nrt += 1
        except Exception: pass
    made[key] = nid
    L.append('%s view %s, %d roomtags' % (key, nid.Value, nrt))
# mech keynotes into the mech view
mv = doc.GetElement(made['mech'])
placed = []
for (n, ex, ey, dx, dy) in TAGS1:
    try:
        fi = doc.Create.NewFamilyInstance(_XYZ(ex + dx, ey + dy, 0), sym, mv)
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
        placed.append((fi.Id, n))
    except Exception as ex2:
        L.append('tag %s fail %s' % (n, str(ex2)[:40]))
doc.Regenerate()
for eid, n in placed:
    p2 = doc.GetElement(eid).LookupParameter('TEXT')
    if p2 and p2.AsString() != n: p2.Set(n)
# verify tags did NOT leak into the primary/dependent
leak = 0
for e in FEC(doc, ElementId(718579)).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name == 'TAG LABEL': leak += 1
    except Exception: pass
L.append('placed %d mech tags; leak into 718579 = %d' % (len(placed), leak))
# place viewports
for sn, key, cx, cy in [('A200', 'mech', 2.36, 1.42), ('A201', 'elec', 1.76, 1.30)]:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn:
            vp = Viewport.Create(doc, s.Id, made[key], _XYZ(cx, cy, 0))
            doc.Regenerate()
            try: vp.LabelOffset = _XYZ(0.06, -0.05, 0)
            except Exception: pass
            ol = vp.GetBoxOutline()
            L.append('%s vp (%.2f,%.2f)-(%.2f,%.2f)' % (sn, ol.MinimumPoint.X,
                     ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

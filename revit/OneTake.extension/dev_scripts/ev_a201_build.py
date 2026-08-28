# A201: duplicate floor plans as elec views, room-tag, view range up, swap vps;
# hide elec/light cats in arch + mech + roof plans.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, ViewDuplicateOption, ElementId, XYZ as _XYZ,
                               UV, LinkElementId, Category, BoundingBoxXYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP,
                               PlanViewPlane)
from System.Collections.Generic import List
L = []
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A201': sh = s
oldvp = []
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    if 'Electric' in v.Name: oldvp.append(vp.Id)
seccat = Category.GetCategory(doc, BIC.OST_Sections)
elevcat = Category.GetCategory(doc, BIC.OST_Elev)
ecat = Category.GetCategory(doc, BIC.OST_ElectricalFixtures)
lcat = Category.GetCategory(doc, BIC.OST_LightingFixtures)
t = Transaction(doc, 'OneTake: A201 build'); _prep(t); t.Start()
made = []
for srcid, name, title, cx in [
        (718579, 'ADU 1st Floor Elec Plan', '1st Floor Electrical Plan', 1.76),
        (1715860, 'ADU 2nd Floor Elec Plan', '2nd Floor Electrical Plan', 0.66)]:
    src = doc.GetElement(ElementId(srcid))
    nid = src.Duplicate(ViewDuplicateOption.Duplicate)
    nv = doc.GetElement(nid)
    nv.Name = name
    nv.Scale = 64
    p = nv.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    scb = src.CropBox
    nb = BoundingBoxXYZ(); nb.Transform = scb.Transform
    nb.Min = scb.Min; nb.Max = scb.Max
    nv.CropBox = nb
    for c in [seccat, elevcat]:
        try: nv.SetCategoryHidden(c.Id, True)
        except Exception: pass
    try:
        vr = nv.GetViewRange()
        vr.SetOffset(PlanViewPlane.TopClipPlane, 10.5)
        nv.SetViewRange(vr)
    except Exception as ex:
        L.append('range %s' % str(ex)[:40])
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
    made.append((nid, cx))
    L.append('%s: %d room tags' % (name, nrt))
if oldvp: doc.Delete(List[ElementId](oldvp)); L.append('removed %d old vps' % len(oldvp))
doc.Regenerate()
for nid, cx in made:
    vp = Viewport.Create(doc, sh.Id, nid, _XYZ(cx, 1.30, 0))
    doc.Regenerate()
    try: vp.LabelOffset = _XYZ(0.06, -0.05, 0)
    except Exception: pass
    ol = vp.GetBoxOutline()
    L.append('vp (%.2f,%.2f)-(%.2f,%.2f)' % (ol.MinimumPoint.X, ol.MinimumPoint.Y,
                                             ol.MaximumPoint.X, ol.MaximumPoint.Y))
# hide elec/light categories in non-elec plans
for nm in ['1st Floor Plan', '2nd FLoor Level', 'ADU 1st Floor Mech Plan',
           'ADU 2nd Floor Mech Plan', 'Roof Deck Level']:
    v = getview(nm)
    if v is None: continue
    for c in [ecat, lcat]:
        try: v.SetCategoryHidden(c.Id, True)
        except Exception as ex: L.append('%s hide %s' % (nm, str(ex)[:30]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

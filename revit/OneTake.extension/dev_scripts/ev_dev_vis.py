# Device visibility pass:
# - move new downlights to z = level + 3.5 (below cut plane)
# - elec views: ensure elec/light categories visible; annotation crop on
# - A101 2nd floor + 2nd mech view: hide elec/light
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Category,
                               XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
L = []
ecat = Category.GetCategory(doc, BIC.OST_ElectricalFixtures)
lcat = Category.GetCategory(doc, BIC.OST_LightingFixtures)
t = Transaction(doc, 'OneTake: device vis'); _prep(t); t.Start()
n = 0
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name != 'Downlight - Recessed Can': continue
        bb = e.get_BoundingBox(None)
        if bb is None: continue
        cx = (bb.Min.X + bb.Max.X) / 2
        cy = (bb.Min.Y + bb.Max.Y) / 2
        if not (1120 < cx < 1200 and 80 < cy < 128): continue
        lvl = doc.GetElement(e.LevelId)
        p = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
        if p and not p.IsReadOnly:
            p.Set(3.5); n += 1
    except Exception as ex:
        L.append('can %s' % str(ex)[:40])
L.append('%d cans lowered' % n)
for vid, show in [(2244950, True), (2244908, True), (1715860, False), (2244778, False)]:
    v = doc.GetElement(ElementId(vid))
    for c in [ecat, lcat]:
        try: v.SetCategoryHidden(c.Id, not show)
        except Exception as ex: L.append('%s %s' % (vid, str(ex)[:30]))
    if show:
        p = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
        if p and not p.IsReadOnly: p.Set(1)
    L.append('%s -> elec %s' % (v.Name, 'SHOWN' if show else 'hidden'))
doc.Regenerate(); t.Commit()
# count devices now visible in each elec view
for vid in [2244950, 2244908]:
    v = doc.GetElement(ElementId(vid))
    ne = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType()))
    nl = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType()))
    L.append('%s: elec=%d light=%d' % (v.Name, ne, nl))
result = '\n'.join(L)

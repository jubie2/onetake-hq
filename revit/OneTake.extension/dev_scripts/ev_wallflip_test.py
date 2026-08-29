# Every affected wall has ALL its devices facing the wrong way, so flipping the WALL
# should fix them wholesale. Test on a partition with no doors/windows first, and
# report how many inserts each affected wall carries.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Wall,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
WALLS = [2189094, 2189148, 2189181, 2194765, 2200152, 2204667, 2206399, 2206505,
         2209664, 2210131]
L = []
for wid in WALLS:
    w = doc.GetElement(ElementId(wid))
    if w is None: L.append('%s missing' % wid); continue
    ins = 0
    try: ins = len(list(w.FindInserts(True, True, True, True)))
    except Exception as ex: ins = -1
    loc = ''
    try:
        p = w.get_Parameter(BIP.WALL_KEY_REF_PARAM)
        loc = p.AsValueString() if p else '?'
    except Exception: pass
    L.append('  wall %-9s %-22s inserts=%-3s locationline=%s' % (
        wid, w.Name[:22], ins, loc))
# --- test flip on 2194765 (single device, expect no inserts) ---
tw = doc.GetElement(ElementId(2194765))
dev = None
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        if e.Host and e.Host.Id.Value == 2194765: dev = e; break
    except Exception: pass
if dev is not None:
    L.append('before: device %s facing (%.2f,%.2f)' % (
        dev.Id.Value, dev.FacingOrientation.X, dev.FacingOrientation.Y))
    c = tw.Location.Curve
    L.append('  wall curve (%.2f,%.2f)->(%.2f,%.2f)' % (
        c.GetEndPoint(0).X, c.GetEndPoint(0).Y, c.GetEndPoint(1).X, c.GetEndPoint(1).Y))
    t = Transaction(doc, 'OneTake: wall flip test'); _prep(t); t.Start()
    try:
        tw.Flip()
        doc.Regenerate()
        d2 = doc.GetElement(dev.Id)
        c2 = tw.Location.Curve
        L.append('after flip: facing (%.2f,%.2f)  wall curve (%.2f,%.2f)->(%.2f,%.2f)' % (
            d2.FacingOrientation.X, d2.FacingOrientation.Y,
            c2.GetEndPoint(0).X, c2.GetEndPoint(0).Y,
            c2.GetEndPoint(1).X, c2.GetEndPoint(1).Y))
    except Exception as ex:
        L.append('flip FAILED %s' % str(ex)[:70])
    t.RollBack()
result = '\n'.join(L)

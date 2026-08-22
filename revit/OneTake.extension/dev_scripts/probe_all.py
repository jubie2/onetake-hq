# Facts needed for: ADU door/window schedule, drawing list, mech+elec devices, framing.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ViewSchedule, ViewSheet, Level,
                               FamilyInstance, SpatialElement, View)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
def ctr(e):
    b = e.get_BoundingBox(None)
    if b is None: return None
    return ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0, (b.Min.Z + b.Max.Z) / 2.0)
def inadu(e):
    c = ctr(e)
    return c is not None and X0 <= c[0] <= X1 and Y0 <= c[1] <= Y1

L.append('=== ADU doors: level / phase / mark / type')
seen = {}
for e in FEC(doc).OfCategory(BIC.OST_Doors).WhereElementIsNotElementType():
    if not inadu(e): continue
    lv = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else '?'
    ph = e.get_Parameter(BIP.PHASE_CREATED)
    ph = doc.GetElement(ph.AsElementId()).Name if ph and ph.AsElementId().IntegerValue > 0 else '?'
    mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
    tn = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
    k = (lv, ph)
    seen[k] = seen.get(k, 0) + 1
    if len(L) < 12: L.append('   %s | lvl %s | phase %s | mark %s' % (tn, lv, ph, mk.AsString() if mk else ''))
L.append('   door level/phase counts: %s' % seen)
L.append('=== ADU windows level/phase counts')
seen = {}
for e in FEC(doc).OfCategory(BIC.OST_Windows).WhereElementIsNotElementType():
    if not inadu(e): continue
    lv = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else '?'
    ph = e.get_Parameter(BIP.PHASE_CREATED)
    ph = doc.GetElement(ph.AsElementId()).Name if ph and ph.AsElementId().IntegerValue > 0 else '?'
    seen[(lv, ph)] = seen.get((lv, ph), 0) + 1
L.append('   %s' % seen)
L.append('=== main-building doors level/phase counts (for contrast)')
seen = {}
for e in FEC(doc).OfCategory(BIC.OST_Doors).WhereElementIsNotElementType():
    if inadu(e): continue
    lv = doc.GetElement(e.LevelId).Name if e.LevelId and e.LevelId.IntegerValue > 0 else '?'
    ph = e.get_Parameter(BIP.PHASE_CREATED)
    ph = doc.GetElement(ph.AsElementId()).Name if ph and ph.AsElementId().IntegerValue > 0 else '?'
    seen[(lv, ph)] = seen.get((lv, ph), 0) + 1
L.append('   %s' % seen)
L.append('=== DOOR SCHEDULE / WINDOWS SCHEDULE / Drawing List definition')
for nm in ('DOOR SCHEDULE', 'WINDOWS SCHEDULE', 'Drawing List'):
    for s in FEC(doc).OfClass(ViewSchedule):
        if s.Name != nm: continue
        d = s.Definition
        L.append('  %s: %d fields' % (nm, d.GetFieldCount()))
        fs = []
        for i in range(d.GetFieldCount()):
            fs.append(d.GetField(i).GetName())
        L.append('     fields: %s' % ', '.join(fs))
        L.append('     filters: %d' % d.GetFilterCount())
        for i in range(d.GetFilterCount()):
            f = d.GetFilter(i)
            try: fn = d.GetField(f.FieldId).GetName()
            except Exception: fn = '?'
            L.append('        %s %s' % (fn, f.FilterType))
L.append('=== ADU rooms')
for e in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
    try:
        if e.Area < 1: continue
        c = ctr(e)
        if c is None or not (X0 <= c[0] <= X1 and Y0 <= c[1] <= Y1): continue
        lv = e.Level.Name if e.Level else '?'
        L.append('   %-14s %6.0f sf  lvl %-16s at (%.1f, %.1f)' % (
            e.get_Parameter(BIP.ROOM_NAME).AsString(), e.Area, lv, c[0], c[1]))
    except Exception: pass
result = '\n'.join(L)

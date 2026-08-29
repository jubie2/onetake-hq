# Rebuild the north 1st-floor wall destroyed by the curve-reversal experiment,
# with its door, 3 windows (types/sills/marks from the A102 schedule) and 6 devices.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Wall, Line,
                               XYZ as _XYZ, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
WALL_TYPE = 2030414          # Generic - 6" NEW 2
LVL = 30                     # 1st Floor Level (elev 0.67)
A = _XYZ(1127.02, 110.32, 0.67)
B = _XYZ(1164.25, 119.81, 0.67)
HEIGHT = 10.0
sib = doc.GetElement(ElementId(2189094))
PHASE = sib.get_Parameter(BIP.PHASE_CREATED).AsElementId()
lvl = doc.GetElement(ElementId(LVL))
# (symbol id, x, y, sill above level, mark, kind)
OPENINGS = [
 (141640,  1152.6, 116.8, 0.0, '106', 'door'),    # Sliding-2 panel 72" x 82"
 (668499,  1133.0, 111.9, 2.5, '04',  'win'),     # Gliding 2x5  36" x 60"
 (2231970, 1141.7, 114.1, 5.5, '03',  'win'),     # Gliding 2x3  36" x 24"
 (713872,  1159.4, 118.6, 3.0, '02',  'win'),     # Gliding 2x3  48" x 48"
]
def sym_by_family(famname, cat):
    for s in FEC(doc).OfClass(__import__('Autodesk').Revit.DB.FamilySymbol).OfCategory(cat):
        if s.Family.Name == famname: return s
DEVICES = [
 ('Outlet-GFI',    1156.6, 117.9, 3.0),
 ('Outlet-GFI',    1158.5, 118.3, 3.0),
 ('Outlet-GFI',    1160.4, 118.8, 3.0),
 ('Outlet-GFI',    1162.2, 119.3, 3.0),
 ('Outlet-Duplex', 1133.5, 112.0, 1.5),
 ('Switch-Single', 1154.9, 117.4, 3.8),
]
L = []
t = Transaction(doc, 'OneTake: rebuild north wall'); _prep(t); t.Start()
w = Wall.Create(doc, Line.CreateBound(A, B), ElementId(WALL_TYPE), ElementId(LVL),
                HEIGHT, 0.0, False, False)
p = w.get_Parameter(BIP.PHASE_CREATED)
if p and not p.IsReadOnly: p.Set(PHASE)
doc.Regenerate()
L.append('wall rebuilt: id %s  (%.2f,%.2f)->(%.2f,%.2f) height %.1f' % (
    w.Id.Value, A.X, A.Y, B.X, B.Y, HEIGHT))
for symid, x, y, sill, mark, kind in OPENINGS:
    s = doc.GetElement(ElementId(symid))
    if s is None: L.append('  symbol %s MISSING' % symid); continue
    if not s.IsActive: s.Activate(); doc.Regenerate()
    try:
        fi = doc.Create.NewFamilyInstance(_XYZ(x, y, 0.67 + sill), s, w, lvl,
                                          StructuralType.NonStructural)
        doc.Regenerate()
        if kind == 'win':
            ps = fi.get_Parameter(BIP.INSTANCE_SILL_HEIGHT_PARAM)
            if ps and not ps.IsReadOnly: ps.Set(sill)
        pm = fi.get_Parameter(BIP.ALL_MODEL_MARK)
        if pm and not pm.IsReadOnly: pm.Set(mark)
        pc = fi.get_Parameter(BIP.ALL_MODEL_INSTANCE_COMMENTS)
        if pc and not pc.IsReadOnly: pc.Set('ADU')
        pp = fi.get_Parameter(BIP.PHASE_CREATED)
        if pp and not pp.IsReadOnly: pp.Set(PHASE)
        doc.Regenerate()
        L.append('  %-4s mark %-4s id %s  %s' % (kind, mark, fi.Id.Value,
                                                 s.Family.Name[:22]))
    except Exception as ex:
        L.append('  %s %s FAILED %s' % (kind, mark, str(ex)[:60]))
for famname, x, y, zoff in DEVICES:
    s = sym_by_family(famname, BIC.OST_ElectricalFixtures)
    if s is None: L.append('  %s symbol missing' % famname); continue
    if not s.IsActive: s.Activate(); doc.Regenerate()
    try:
        fi = doc.Create.NewFamilyInstance(_XYZ(x, y, 0.67 + zoff), s, w, lvl,
                                          StructuralType.NonStructural)
        doc.Regenerate()
        pe = fi.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
        if pe and not pe.IsReadOnly: pe.Set(zoff)
        pp = fi.get_Parameter(BIP.PHASE_CREATED)
        if pp and not pp.IsReadOnly: pp.Set(PHASE)
        L.append('  device %-14s id %s at (%.1f,%.1f)' % (famname, fi.Id.Value, x, y))
    except Exception as ex:
        L.append('  device %s FAILED %s' % (famname, str(ex)[:60]))
doc.Regenerate(); t.Commit()
n1 = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: pt = e.Location.Point
    except Exception: continue
    if pt is not None and 1120 < pt.X < 1200 and 78 < pt.Y < 128 and pt.Z < 10: n1 += 1
L.append('1st-floor devices now: %d (was 26 before the damage)' % n1)
result = '\n'.join(L)

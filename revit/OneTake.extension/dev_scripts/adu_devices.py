# Populate the ADU with electrical + mechanical devices, matching the main building's families.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, FamilySymbol, Level, View,
                               SpatialElementBoundaryOptions, XYZ as _XYZ, Wall,
                               ElementId, Structure)
from Autodesk.Revit.DB.Structure import StructuralType
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
L = []

def sym(fam, typ=None):
    for s in FEC(doc).OfClass(FamilySymbol):
        try:
            if s.Family.Name != fam: continue
            if typ is None: return s
            if (s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == typ: return s
        except Exception: pass
    return None

S = {
 'outlet':  sym('Outlet-Duplex', 'Single'),
 'gfi':     sym('Outlet-GFI', 'Single'),
 'switch':  sym('Switch-Single', 'Single'),
 'light':   sym('High_efficacy_Light', 'CARBONMONOXIDE'),
 'vanity':  sym("Fluor-vanity-light_2'", 'CARBONMONOXIDE'),
 'smoke':   sym('Smoke', 'Smoke%20Detector[1]'),
 'co':      sym('Smoke', 'CARBONMONOXIDE'),
 'register':sym('Supply Register-Floor 2 way', '5" x 14"'),
 'wh':      sym('Water Heater', 'Water Heater'),
}
for k in S:
    L.append('symbol %-9s %s' % (k, 'OK' if S[k] else 'MISSING'))
if any(S[k] is None for k in S):
    result = '\n'.join(L) + '\nABORT: missing symbols'
else:
    # existing switch mounting height, for matching
    sh = None
    for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name != 'Switch-Single': continue
            p = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
            sh = p.AsDouble() if p and p.HasValue else None
            break
        except Exception: pass
    OUT_Z, SW_Z = 0.8125, (sh if sh else 4.0)
    L.append('mounting: outlets %.3f ft, switches %.3f ft above level' % (OUT_Z, SW_Z))

    evw = None; mvw = None
    for v in FEC(doc).OfClass(View):
        if v.IsTemplate: continue
        if v.Name == 'ADU - Electrical Plan': evw = v
        if v.Name == 'ADU - Mechanical Plan': mvw = v

    lvls = {}
    for lv in FEC(doc).OfClass(Level): lvls[lv.Name] = lv

    rooms = []
    for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
        try:
            if r.Area < 1: continue
            b = r.get_BoundingBox(None)
            cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
            if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
            rooms.append((r, r.get_Parameter(BIP.ROOM_NAME).AsString(), cx, cy))
        except Exception: pass
    L.append('ADU rooms found: %d' % len(rooms))

    GFI_ROOMS = ('Kitchen', 'Bath room')
    SMOKE_ROOMS = ('Bed-1', 'Bed-2', 'Family')
    plan = {'outlet': [], 'gfi': [], 'switch': [], 'light': [], 'vanity': [],
            'smoke': [], 'co': [], 'register': [], 'wh': []}
    opt = SpatialElementBoundaryOptions()
    for r, nmr, cx, cy in rooms:
        lv = r.Level
        z = lv.Elevation
        c = _XYZ(cx, cy, 0)
        # ceiling light / vanity
        plan['vanity' if nmr == 'Bath room' else 'light'].append((lv, _XYZ(cx, cy, 0)))
        if nmr in SMOKE_ROOMS:
            plan['smoke'].append((lv, _XYZ(cx + 1.2, cy + 1.2, 0)))
        if nmr == 'Family':
            plan['co'].append((lv, _XYZ(cx - 1.2, cy + 1.2, 0)))
        if r.Area > 40:
            plan['register'].append((lv, _XYZ(cx + 1.5, cy - 1.5, z)))
        # outlets on boundary walls
        want = 4 if r.Area > 150 else (3 if r.Area > 90 else (2 if r.Area > 40 else 0))
        kind = 'gfi' if nmr in GFI_ROOMS else 'outlet'
        got = 0
        try: loops = r.GetBoundarySegments(opt)
        except Exception: loops = []
        segs = []
        for loop in loops:
            for bs in loop:
                w = doc.GetElement(bs.ElementId)
                if not isinstance(w, Wall): continue
                cv = bs.GetCurve()
                if cv.Length < 4.0: continue
                segs.append((cv.Length, cv, w))
        segs.sort(key=lambda z2: -z2[0])
        for ln, cv, w in segs:
            if got >= want: break
            m = cv.Evaluate(0.5, True)
            out = _XYZ(m.X - cx, m.Y - cy, 0)
            g = (out.X ** 2 + out.Y ** 2) ** 0.5
            if g < 1e-6: continue
            p = _XYZ(m.X + out.X / g * 0.15, m.Y + out.Y / g * 0.15, z + OUT_Z)
            plan[kind].append((lv, p, w))
            got += 1
        # one switch per room that has a light, on the longest wall near its end
        if segs and r.Area > 12:
            ln, cv, w = segs[0]
            q = cv.Evaluate(0.15, True)
            out = _XYZ(q.X - cx, q.Y - cy, 0)
            g = (out.X ** 2 + out.Y ** 2) ** 0.5
            if g > 1e-6:
                plan['switch'].append((lv, _XYZ(q.X + out.X / g * 0.15,
                                                q.Y + out.Y / g * 0.15, z + SW_Z), w))
    # one water heater per floor, in the bigger closet
    for lname in ('1st Floor Level', '2nd FLoor Plan'):
        lv = lvls.get(lname)
        if lv: plan['wh'].append((lv, _XYZ(1170.2, -147.0, lv.Elevation)))

    for k in plan: L.append('  %-9s %d' % (k, len(plan[k])))

    if not dry:
        t = Transaction(doc, 'OneTake: ADU devices'); _prep(t); t.Start()
        for k in S:
            if not S[k].IsActive: S[k].Activate()
        doc.Regenerate()
        made = {}
        for k in ('outlet', 'gfi', 'switch'):
            n = 0
            for item in plan[k]:
                lv, p, w = item
                try:
                    doc.Create.NewFamilyInstance(p, S[k], w, lv, StructuralType.NonStructural); n += 1
                except Exception as ex:
                    L.append('   %s fail %s' % (k, str(ex)[:45]))
            made[k] = n
        for k in ('register', 'wh'):
            n = 0
            for lv, p in plan[k]:
                try:
                    doc.Create.NewFamilyInstance(p, S[k], lv, StructuralType.NonStructural); n += 1
                except Exception as ex:
                    L.append('   %s fail %s' % (k, str(ex)[:45]))
            made[k] = n
        for k in ('light', 'vanity', 'smoke', 'co'):
            n = 0
            for lv, p in plan[k]:
                v = evw
                try:
                    doc.Create.NewFamilyInstance(p, S[k], v); n += 1
                except Exception as ex:
                    L.append('   %s fail %s' % (k, str(ex)[:45]))
            made[k] = n
        doc.Regenerate(); t.Commit()
        L.append('created: %s' % made)
    result = '\n'.join(L)

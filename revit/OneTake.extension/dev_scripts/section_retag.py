# Rebuild section keynotes as TAG LABEL + leader, split evenly left/right like the
# approved A102. Wipes the old drawn bubbles (arcs+digit notes+leader lines).
# Numbers per the KEYNOTES SECTION legend:
# 1 roof shingle  2 stucco  3 slab  4 gyp bd  5 weep screed  6 PT bottom plate
# 7 dbl top plate 8 studs   9 truss 10 R-15 wall batt 11 R-30 ceiling batt 12 footing
# args {"view":"ADU - Section 1","dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               CurveElement, Arc, Line, FamilySymbol, Wall, RoofBase,
                               BuiltInCategory as BIC, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
import re
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
R = 0.55
dry = args.get('dry', True)
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s' % nm]
bb = v.CropBox; tfm = bb.Transform; inv = tfm.Inverse
# building extent in view coords from the ADU roof (walls pick up stray fragments);
# subtract the 1'-6" overhang to land on the wall faces
uw = []; roofz = []
for e in FEC(doc, v.Id).OfClass(RoofBase):
    b = e.get_BoundingBox(None)
    if b is None: continue
    c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, (b.Min.Z + b.Max.Z) / 2)
    if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
    roofz = [b.Min.Z, b.Max.Z]
    for px in (b.Min.X, b.Max.X):
        for py in (b.Min.Y, b.Max.Y):
            q = inv.OfPoint(_XYZ(px, py, c.Z))
            uw.append(q.X)
uL, uR = min(uw) + 1.5, max(uw) - 1.5
um = (uL + uR) / 2.0
# local Y is world Z shifted by the crop transform origin - compute the offset
zoff = inv.OfPoint(_XYZ(1171.0, -138.0, 0.0)).Y
def lz(wz): return wz + zoff
L.append('uL %.1f uR %.1f zoff %.1f roofz %s' % (uL, uR, zoff, roofz))
# (num, tag u,z, end u,z) - left column then right column then slab below
TL, TR = uL - 3.2, uR + 3.2
SPEC = [
 ('1',  TL, lz(24.6),  uL + 2.6, lz(23.0)),
 ('7',  TL, lz(20.5),  uL + 0.6, lz(20.4)),
 ('2',  TL, lz(14.8),  uL + 0.15, lz(14.8)),
 ('6',  TL, lz(2.2),   uL + 0.6, lz(1.1)),
 ('5',  TL, lz(0.2),   uL + 0.15, lz(0.4)),
 ('9',  TR, lz(23.6),  uR - 2.6, lz(22.4)),
 ('11', TR, lz(21.2),  uR - 5.0, lz(20.9)),
 ('8',  TR, lz(16.8),  uR - 0.5, lz(16.8)),
 ('4',  TR, lz(13.2),  uR - 0.9, lz(13.2)),
 ('10', TR, lz(6.4),   uR - 0.45, lz(6.4)),
 ('12', TR, lz(0.3),   uR - 0.3, lz(-0.4)),
 ('3',  um, lz(-2.3),  um, lz(0.5)),
]
# clamp inside crop
cu0, cu1 = bb.Min.X + 1.0, bb.Max.X - 1.0
cz0, cz1 = bb.Min.Y + 0.8, bb.Max.Y - 0.8
jobs = []
for num, tu, tz, eu, ez in SPEC:
    tu = max(cu0, min(cu1, tu)); tz = max(cz0, min(cz1, tz))
    jobs.append((num, tu, tz, eu, ez))
    L.append('  %-2s tag (%.1f,%.1f) -> end (%.1f,%.1f)' % (num, tu, tz, eu, ez))
# find old drawn bubbles
arcs = []; lines = []; notes = []; oldtags = []
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    if isinstance(e, CurveElement):
        c = e.GeometryCurve
        if isinstance(c, Arc) and abs(c.Radius - R) < 0.05:
            arcs.append((e.Id, c.Center))
        elif isinstance(c, Line):
            lines.append((e.Id, c.GetEndPoint(0), c.GetEndPoint(1)))
    elif isinstance(e, TextNote):
        m = re.match(r'^\s*(\d{1,2})\s*$', (e.Text or '').replace('\r', ' ').replace('/', ' '))
        if m: notes.append((e.Id, e.Coord))
    else:
        try:
            if e.Category and e.Category.Id.Value == int(BIC.OST_GenericAnnotation) \
               and e.Symbol.Family.Name == 'TAG LABEL':
                oldtags.append(e.Id)
        except Exception: pass
kill = [a[0] for a in arcs] + oldtags
for nid, p in notes:
    if any(p.DistanceTo(c) < 1.5 for _, c in arcs): kill.append(nid)
for lid, p0, p1 in lines:
    if any(min(p0.DistanceTo(c), p1.DistanceTo(c)) < R + 0.35 for _, c in arcs):
        kill.append(lid)
L.append('wiping %d elems (%d arcs, %d tags)' % (len(kill), len(arcs), len(oldtags)))
if not dry:
    sym = None
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
        if s.Family.Name == 'TAG LABEL': sym = s; break
    t = Transaction(doc, 'OneTake: section tags %s' % nm); _prep(t); t.Start()
    if kill: doc.Delete(List[ElementId](kill))
    if not sym.IsActive:
        sym.Activate(); doc.Regenerate()
    def W(u, z): return tfm.OfPoint(_XYZ(u, z, 0.0))
    placed = []
    for num, tu, tz, eu, ez in jobs:
        try:
            fi = doc.Create.NewFamilyInstance(W(tu, tz), sym, v)
            doc.Regenerate()
            e = doc.GetElement(fi.Id)
            e.addLeader()
            doc.Regenerate()
            try: lds = list(e.GetLeaders())
            except Exception:
                lds = []; la = e.Leaders
                for i in range(la.Size): lds.append(la.get_Item(i))
            if lds:
                lds[-1].End = W(eu, ez)
                elb = tu + (1.2 if eu > tu else -1.2)
                lds[-1].Elbow = W(elb, tz)
            placed.append((fi.Id, num))
        except Exception as ex:
            L.append('  %s FAIL %s' % (num, str(ex)[:70]))
    doc.Regenerate()
    for eid, num in placed:
        p2 = doc.GetElement(eid).LookupParameter('TEXT')
        if p2 and p2.AsString() != num: p2.Set(num)
    doc.Regenerate(); t.Commit()
    bad = ['%s got %s' % (num, doc.GetElement(eid).LookupParameter('TEXT').AsString())
           for eid, num in placed
           if doc.GetElement(eid).LookupParameter('TEXT').AsString() != num]
    L.append('placed %d%s' % (len(placed), ('  BAD: ' + ','.join(bad)) if bad else ', all TEXT verified'))
result = '\n'.join(L)

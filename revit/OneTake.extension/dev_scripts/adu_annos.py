# Place light / smoke / CO annotation symbols per floor into the matching ADU electrical view.
# Symbol note: in this model the 'Smoke' family type CARBONMONOXIDE draws the SD marker and
# type Smoke%20Detector[1] draws the C marker - verified on screen, names are misleading.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, FamilySymbol, View, XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
L = []
def sym(fam, typ):
    for s in FEC(doc).OfClass(FamilySymbol):
        try:
            if s.Family.Name == fam and (s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == typ:
                return s
        except Exception: pass
    return None
S = {'light': sym('High_efficacy_Light', 'CARBONMONOXIDE'),
     'vanity': sym("Fluor-vanity-light_2'", 'CARBONMONOXIDE'),
     'smoke': sym('Smoke', 'CARBONMONOXIDE'),
     'co': sym('Smoke', 'Smoke%20Detector[1]')}
VIEWS = {}
for v in FEC(doc).OfClass(View):
    if v.IsTemplate: continue
    if v.Name == 'ADU - 1st Floor Electrical Plan': VIEWS['1st Floor Level'] = v
    if v.Name == 'ADU - 2nd Floor Electrical Plan': VIEWS['2nd FLoor Plan'] = v
L.append('views: %s' % dict((k, str(VIEWS[k].Id)) for k in VIEWS))
SMOKE_ROOMS = ('Bed-1', 'Bed-2', 'Family')
jobs = []
for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
    try:
        if r.Area < 1: continue
        b = r.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        lvn = r.Level.Name
        v = VIEWS.get(lvn)
        if v is None: continue
        nmr = r.get_Parameter(BIP.ROOM_NAME).AsString()
        jobs.append((v, 'vanity' if nmr == 'Bath room' else 'light', _XYZ(cx, cy, 0)))
        if nmr in SMOKE_ROOMS:
            jobs.append((v, 'smoke', _XYZ(cx + 1.2, cy + 1.2, 0)))
        if nmr == 'Family':
            jobs.append((v, 'co', _XYZ(cx - 1.2, cy + 1.2, 0)))
    except Exception: pass
cnt = {}
for v, k, p in jobs: cnt['%s/%s' % (v.Name[6:20], k)] = cnt.get('%s/%s' % (v.Name[6:20], k), 0) + 1
for k in sorted(cnt): L.append('  %-30s %d' % (k, cnt[k]))
if not dry:
    t = Transaction(doc, 'OneTake: ADU annotations'); _prep(t); t.Start()
    for k in S:
        if S[k] and not S[k].IsActive: S[k].Activate()
    doc.Regenerate()
    n = 0
    for v, k, p in jobs:
        try:
            doc.Create.NewFamilyInstance(p, S[k], v); n += 1
        except Exception as ex:
            L.append('  fail %s %s' % (k, str(ex)[:45]))
    doc.Regenerate(); t.Commit()
    L.append('placed %d' % n)
result = '\n'.join(L)

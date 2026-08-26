# ADU-4 roof sheet per approved A103: leader callouts on the roof plan, roof framing
# plan moved over from ADU-8, shingle spec block under the legend.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, BuiltInParameter as BIP,
                               ElementId, XYZ as _XYZ, Line)
from System.Collections.Generic import List
import math
dry = args.get('dry', True)
L = []
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
def getsheet(num):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == num: return s
    return None
rp = getview('ADU - Roof Plan')
s4 = getsheet('ADU-4'); s8 = getsheet('ADU-8')
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
# framing viewport on ADU-8
fvp = None
for vpid in s8.GetAllViewports():
    vp = doc.GetElement(vpid)
    if doc.GetElement(vp.ViewId).Name == 'ADU - Roof Framing Plan': fvp = vp
L.append('framing vp %s, texttype %s' % (fvp.Id.Value if fvp else 'GONE',
                                         tt.Id.Value if tt else 'MISSING'))
CALLS = [
 ('FUTURE SOLAR PANELS\n(SEPARATE PERMIT)', (1191.0, -151.5),
  (1190.3, -146.8), (1184.5, -144.5)),
 ('NEW ROOF SHINGLE', (1191.0, -133.5),
  (1190.3, -132.3), (1184.8, -131.0)),
]
if not dry:
    t = Transaction(doc, 'OneTake: roof sheet'); _prep(t); t.Start()
    # 1. stale/off-crop notes
    doc.Delete(List[ElementId]([ElementId(i) for i in (2188216, 2194735, 2194734)]))
    # 2. leader callouts on the roof plan
    BARB = 1.1; BA = math.radians(17)
    for txt, tp, p0, p1 in CALLS:
        a = _XYZ(p0[0], p0[1], 0); b = _XYZ(p1[0], p1[1], 0)
        doc.Create.NewDetailCurve(rp, Line.CreateBound(a, b))
        back = math.atan2(a.Y - b.Y, a.X - b.X)
        for sgn in (1, -1):
            ang = back + sgn * BA
            doc.Create.NewDetailCurve(rp, Line.CreateBound(
                b, _XYZ(b.X + math.cos(ang) * BARB, b.Y + math.sin(ang) * BARB, 0)))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Left
        TextNote.Create(doc, rp.Id, _XYZ(tp[0], tp[1], 0), txt, o)
    # 3. move framing viewport ADU-8 -> ADU-4
    if fvp is not None:
        vtid = fvp.GetTypeId(); vid = fvp.ViewId
        doc.Delete(fvp.Id)
        doc.Regenerate()
        nvp = Viewport.Create(doc, s4.Id, vid, _XYZ(1.55, 1.21, 0))
        try: nvp.ChangeTypeId(vtid)
        except Exception: pass
        nvp.SetBoxCenter(_XYZ(1.55, 1.21, 0))
        # respace the two left on ADU-8
        for vpid in s8.GetAllViewports():
            vp = doc.GetElement(vpid)
            nm = doc.GetElement(vp.ViewId).Name
            if nm == 'ADU - Foundation Plan': vp.SetBoxCenter(_XYZ(0.85, 1.25, 0))
            elif nm == 'ADU - 2nd Floor Framing Plan': vp.SetBoxCenter(_XYZ(1.95, 1.25, 0))
    # 4. shingle spec block on the sheet under the legend
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    TextNote.Create(doc, s4.Id, _XYZ(2.18, 1.55, 0),
        "ROOF SHINGLE SPEC:\nOWENS CORNING (OR EQ.), CLASS 'A'\n"
        "ICC-ESR LISTED / CRRC RATED\nOVER (1) LAYER 30# FELT", o)
    doc.Regenerate(); t.Commit()
    L.append('done')
result = '\n'.join(L)

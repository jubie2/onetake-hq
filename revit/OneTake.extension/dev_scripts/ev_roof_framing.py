# Build the ADU roof framing plan: joists at 16" o.c. spanning the short direction
# of each block, ridge/drag beams, labels; place it on A104 beside the roof plan.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, Viewport,
                               ViewDuplicateOption, ElementId, XYZ as _XYZ, Line,
                               GraphicsStyle, TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, BoundingBoxXYZ, Category,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)
VX, VY = -math.sin(A), math.cos(A)
BX, BY = 1161.1251, 98.8210
def W(s, t): return _XYZ(BX + UX * s + VX * t, BY + UY * s + VY * t, 0)
MAIN = (-27.7, 8.2, -6.0, 19.6)      # s0,s1,t0,t1  - joists span t, beam mid-t
WING = (8.2, 22.5, -1.4, 16.6)       # joists span s
OC = 16.0 / 12.0
L = []
src = doc.GetElement(ElementId(2218677))          # Roof Deck Level plan
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
tt = None
for x in FEC(doc).OfClass(TextNoteType):
    nm = x.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
    if '3/32' in nm: tt = x; break
if tt is None:
    for x in FEC(doc).OfClass(TextNoteType):
        nm = x.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        if '1/8' in nm: tt = x; break
if tt is None: tt = FEC(doc).OfClass(TextNoteType).FirstElement()
t = Transaction(doc, 'OneTake: roof framing plan'); _prep(t); t.Start()
old = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU Roof Framing Plan': old = x
if old is not None:
    doc.Delete(old.Id); doc.Regenerate()
nid = src.Duplicate(ViewDuplicateOption.Duplicate)
nv = doc.GetElement(nid)
nv.Name = 'ADU Roof Framing Plan'
nv.Scale = 64
p = nv.get_Parameter(BIP.VIEW_DESCRIPTION)
if p and not p.IsReadOnly: p.Set('Roof Framing Plan')
scb = src.CropBox
nb = BoundingBoxXYZ(); nb.Transform = scb.Transform
nb.Min = scb.Min; nb.Max = scb.Max
nv.CropBox = nb
nv.CropBoxActive = True
for bic in (BIC.OST_Sections, BIC.OST_Elev, BIC.OST_Furniture, BIC.OST_Casework,
            BIC.OST_PlumbingFixtures, BIC.OST_SpecialityEquipment,
            BIC.OST_ElectricalFixtures, BIC.OST_LightingFixtures, BIC.OST_Dimensions):
    try: nv.SetCategoryHidden(Category.GetCategory(doc, bic).Id, True)
    except Exception: pass
p2 = nv.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
if p2 and not p2.IsReadOnly: p2.Set(1)
doc.Regenerate()
def dline(a, b, dashed=False):
    try:
        ce = doc.Create.NewDetailCurve(nv, Line.CreateBound(a, b))
        if dashed and dash:
            try: ce.LineStyle = dash
            except Exception: pass
        return ce
    except Exception as ex:
        L.append('  line fail %s' % str(ex)[:40]); return None
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Left
def note(s, t2, txt):
    try: TextNote.Create(doc, nv.Id, W(s, t2), txt, o)
    except Exception as ex: L.append('  note fail %s' % str(ex)[:40])
nj = 0
# --- main block: joists span t, spaced along s ---
s0, s1, t0, t1 = MAIN
s = s0 + OC
while s < s1 - 0.05:
    dline(W(s, t0), W(s, t1)); nj += 1
    s += OC
tb = (t0 + t1) / 2.0
for off in (-0.16, 0.16):
    dline(W(s0, tb + off), W(s1, tb + off))
# --- east wing: joists span s, spaced along t ---
s0w, s1w, t0w, t1w = WING
tt2 = t0w + OC
while tt2 < t1w - 0.05:
    dline(W(s0w, tt2), W(s1w, tt2)); nj += 1
    tt2 += OC
for off in (-0.16, 0.16):
    dline(W(s0w + off, t0w), W(s0w + off, t1w))
# --- span arrows + labels ---
dline(W(-10.0, t0 + 1.0), W(-10.0, t1 - 1.0), True)
note(-25.0, tb + 1.2, '2x12 ROOF JOISTS @ 16" O.C.\nSPAN AS SHOWN (TYP.)')
note(s0 + 1.0, tb - 1.6, '4x12 BEAM - SIZE PER STRUCT.')
note(9.0, t1w - 3.0, '2x12 ROOF JOISTS\n@ 16" O.C.')
note(-27.0, t0 - 4.2,
     'ROOF FRAMING PLAN - ALL MEMBER SIZES, CONNECTIONS, HOLD-DOWNS AND\n'
     'SHEAR TRANSFER PER STRUCTURAL ENGINEER\'S CALCULATIONS.\n'
     'ROOF DECK SLOPED 1/4" PER FT MIN. TO DRAINS; SEE ROOF PLAN.')
doc.Regenerate()
# --- place on A104 beside the roof plan ---
sh = None
for s2 in FEC(doc).OfClass(ViewSheet):
    if s2.SheetNumber == 'A104': sh = s2
reftype = None
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v2 = doc.GetElement(vp.ViewId)
    if v2 is not None and v2.Id.Value == 2218677:
        reftype = vp.GetTypeId()
        vp.SetBoxCenter(_XYZ(0.75, 1.25, 0))
        doc.Regenerate()
        ol = vp.GetBoxOutline()
        L.append('Roof Plan moved -> (%.2f,%.2f)-(%.2f,%.2f)' % (
            ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y))
nvp = Viewport.Create(doc, sh.Id, nid, _XYZ(1.95, 1.25, 0))
doc.Regenerate()
if reftype is not None:
    try: nvp.ChangeTypeId(reftype)
    except Exception: pass
try: nvp.LabelOffset = _XYZ(0.06, -0.05, 0)
except Exception: pass
ol = nvp.GetBoxOutline()
L.append('framing view %s: %d joists; vp (%.2f,%.2f)-(%.2f,%.2f)' % (
    nid.Value, nj, ol.MinimumPoint.X, ol.MinimumPoint.Y,
    ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

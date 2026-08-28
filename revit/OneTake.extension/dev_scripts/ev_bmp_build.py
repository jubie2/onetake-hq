# Build Electric Ave BMP site plan: duplicate Site view, draw BMP measures,
# swap into A06 in place of the stale Logan BMP view.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, ViewDuplicateOption, GraphicsStyle,
                               TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, BuiltInParameter as BIP,
                               ElementId, XYZ as _XYZ, Line)
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
site = getview('Site')
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    nm = t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
    if '3/32' in nm or 'ARCH TEXT' in nm.upper(): tt = t2; break
if tt is None:
    tt = FEC(doc).OfClass(TextNoteType).FirstElement()
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
L = []
t = Transaction(doc, 'OneTake: BMP Electric'); _prep(t); t.Start()
nid = site.Duplicate(ViewDuplicateOption.Duplicate)
nv = doc.GetElement(nid)
nv.Name = 'BMP Site Plan - Electric'
p = nv.get_Parameter(BIP.VIEW_DESCRIPTION)
if p and not p.IsReadOnly: p.Set('BMP Site Plan')
L.append('new view %s' % nid.Value)
def line(a, b, dashed=True):
    ce = doc.Create.NewDetailCurve(nv, Line.CreateBound(
        _XYZ(a[0], a[1], 0), _XYZ(b[0], b[1], 0)))
    if dashed and dash:
        try: ce.LineStyle = dash
        except Exception: pass
def rect(x0, y0, x1, y1, dashed=True):
    line((x0, y0), (x1, y0), dashed); line((x1, y0), (x1, y1), dashed)
    line((x1, y1), (x0, y1), dashed); line((x0, y1), (x0, y0), dashed)
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Left
def note(x, y, txt):
    TextNote.Create(doc, nv.Id, _XYZ(x, y, 0), txt, o)
# fiber roll around the ADU work area
rect(1118, 64, 1202, 130, True)
note(1119, 61, 'FIBER ROLL (SE-5) TYP. AT WORK AREA PERIMETER')
# stabilized construction entrance on the existing drive, west of the ADU
rect(1104, 94, 1118, 104, False)
line((1104, 94), (1118, 104), False)
line((1104, 104), (1118, 94), False)
note(1096, 91, 'STABILIZED CONSTRUCTION\nENTRANCE (TC-1)')
# concrete washout + portable toilet east of the ADU
rect(1196, 105, 1201, 110, False)
note(1196, 112, 'CONCRETE WASHOUT (WM-8)')
rect(1196, 96, 1201, 101, False)
note(1196, 93, 'PORTABLE TOILET (WM-9)')
note(1118, 134, 'GRAVEL BAG SILT BARRIER (SE-4) AT DOWNSTREAM CURB / INLETS ON ELECTRIC AVE')
doc.Regenerate()
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A06': sh = s
old = None
for vpid in sh.GetAllViewports():
    vp = doc.GetElement(vpid)
    if doc.GetElement(vp.ViewId).Name == 'BMP Site Plan': old = vp
if old is not None:
    c = old.GetBoxCenter(); tid = old.GetTypeId()
    doc.Delete(old.Id); doc.Regenerate()
    nvp = Viewport.Create(doc, sh.Id, nid, c)
    try: nvp.ChangeTypeId(tid)
    except Exception: pass
    nvp.SetBoxCenter(c)
    try: nvp.LabelOffset = _XYZ(0.3, 0.02, 0)
    except Exception: pass
    L.append('viewport swapped at (%.2f,%.2f)' % (c.X, c.Y))
else:
    L.append('old BMP viewport not found')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

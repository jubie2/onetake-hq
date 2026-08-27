# Build a Keeler BMP site plan: duplicate the Site view, draw BMP measures,
# swap it into A06 in place of the stale Logan view.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, ViewDuplicateOption, GraphicsStyle,
                               TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, BuiltInParameter as BIP,
                               ElementId, XYZ as _XYZ, Line)
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
site = getview('Site')
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n: dash = g; break
L = []
t = Transaction(doc, 'OneTake: BMP Keeler'); _prep(t); t.Start()
nid = site.Duplicate(ViewDuplicateOption.WithDetailing)
nv = doc.GetElement(nid)
nv.Name = 'BMP Site Plan - Keeler'
L.append('new view %s' % nid.Value)
def line(a, b, dashed=True):
    ce = doc.Create.NewDetailCurve(nv, Line.CreateBound(
        _XYZ(a[0], a[1], 0), _XYZ(b[0], b[1], 0)))
    if dashed and dash:
        try: ce.LineStyle = dash
        except Exception: pass
    return ce
def rect(x0, y0, x1, y1, dashed=True):
    line((x0, y0), (x1, y0), dashed); line((x1, y0), (x1, y1), dashed)
    line((x1, y1), (x0, y1), dashed); line((x0, y1), (x0, y0), dashed)
o = TextNoteOptions(tt.Id)
o.HorizontalAlignment = HorizontalTextAlignment.Left
def note(x, y, txt):
    TextNote.Create(doc, nv.Id, _XYZ(x, y, 0), txt, o)
# fiber roll 2 ft inside the property line (PL 1154.9..1204.9, -221.5..-116.5)
rect(1156.9, -219.5, 1202.9, -118.5, True)
note(1160.0, -212.5, 'FIBER ROLL (SE-5) TYP.\nAT PROJECT PERIMETER')
# stabilized construction entrance at the street (south) edge
rect(1186.0, -228.0, 1198.0, -218.0, False)
line((1186.0, -228.0), (1198.0, -218.0), False)
line((1186.0, -218.0), (1198.0, -228.0), False)
note(1183.5, -230.0, 'STABILIZED CONSTRUCTION\nENTRANCE (TC-1)')
# concrete washout + portable toilet near the ADU
rect(1192.0, -140.0, 1197.0, -135.0, False)
note(1197.8, -134.5, 'CONCRETE WASHOUT (WM-8)')
rect(1192.0, -148.0, 1197.0, -143.0, False)
note(1197.8, -142.5, 'PORTABLE TOILET (WM-9)')
note(1156.9, -113.0, 'GRAVEL BAG SILT BARRIER (SE-4) AT DOWNSTREAM CURB / INLETS')
doc.Regenerate()
# swap the A06 viewport
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A06': sh = s; break
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
    L.append('viewport swapped at (%.2f,%.2f)' % (c.X, c.Y))
else:
    L.append('OLD BMP viewport not found')
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

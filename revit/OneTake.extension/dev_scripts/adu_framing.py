# Build ADU foundation + floor framing + roof framing views and sheet ADU-8.
# Framing is DRAFTED with detail lines, matching how S101 is drawn in this model.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewPlan, ViewSheet,
                               ViewDuplicateOption, BuiltInParameter as BIP, ElementId,
                               ImportInstance, XYZ as _XYZ, Line, TextNote, TextNoteOptions,
                               TextNoteType, HorizontalTextAlignment, GraphicsStyle,
                               BuiltInCategory as BIC, Viewport, BoundingBoxXYZ)
from System.Collections.Generic import List
import math
dry = args.get('dry', True)
# ADU exterior footprint, from adu_walls.py
WX0, WX1, WY0, WY1 = 1157.9, 1186.5, -150.3, -125.7
TB = ElementId(311500)
CATS = ['Sections', 'Elevations', 'Callouts', 'Reference Planes', 'Scope Boxes', 'Matchline']
L = ['footprint %.1f x %.1f ft' % (WX1 - WX0, WY1 - WY0)]
SPECS = [('ADU - 1st Floor Plan', 'ADU - Foundation Plan', 'found'),
         ('ADU - 2nd Floor Plan', 'ADU - 2nd Floor Framing Plan', 'floor'),
         ('ADU - Roof Plan', 'ADU - Roof Framing Plan', 'roof')]
for a, b, k in SPECS: L.append('%s -> %s (%s)' % (a, b, k))
if dry:
    result = '\n'.join(L)
else:
    def find(nm):
        for v in FEC(doc).OfClass(View):
            if not v.IsTemplate and v.Name == nm: return v
        return None
    tt = None
    for t2 in FEC(doc).OfClass(TextNoteType):
        if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
            tt = t2; break
    t = Transaction(doc, 'OneTake: ADU framing'); _prep(t); t.Start()
    cats = doc.Settings.Categories
    made_views = []
    for src_n, new_n, kind in SPECS:
        v = find(new_n)
        if v is None:
            src = find(src_n)
            nid = src.Duplicate(ViewDuplicateOption.Duplicate)
            v = doc.GetElement(nid); v.Name = new_n; v.Scale = 48
            v.CropBoxActive = True; v.CropBox = src.CropBox; v.CropBoxVisible = False
            p = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
            if p and not p.IsReadOnly: p.Set(1)
            for cn in CATS:
                try:
                    c = cats.get_Item(cn)
                    if c is not None and v.CanCategoryBeHidden(c.Id): v.SetCategoryHidden(c.Id, True)
                except Exception: pass
            ids = [e.Id for e in FEC(doc, v.Id).OfClass(ImportInstance)
                   if e.CanBeHidden(v) and not e.IsHidden(v)]
            if ids: v.HideElements(List[ElementId](ids))
            doc.Regenerate()
            L.append('created view %s (%s)' % (new_n, v.Id))
        else:
            L.append('view %s already exists' % new_n)
        made_views.append((v, kind))
    doc.Regenerate()

    def mk(v):
        bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
        def on_plane(x, y):
            q = inv.OfPoint(_XYZ(x, y, 0.0))
            return tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
        def dline(x0, y0, x1, y1):
            doc.Create.NewDetailCurve(v, Line.CreateBound(on_plane(x0, y0), on_plane(x1, y1)))
        def note(x, y, txt, ang=0.0):
            o = TextNoteOptions(tt.Id)
            o.HorizontalAlignment = HorizontalTextAlignment.Left
            o.Rotation = ang
            TextNote.Create(doc, v.Id, on_plane(x, y), txt, o)
        return dline, note

    for v, kind in made_views:
        # skip if already drafted
        n_exist = 0
        for e in FEC(doc, v.Id).OfCategory(BIC.OST_Lines):
            n_exist += 1
        if n_exist > 5:
            L.append('%s already has %d detail lines - skipped' % (v.Name, n_exist)); continue
        dline, note = mk(v)
        if kind == 'found':
            F = 0.625                      # 15" continuous footing, centred on the wall
            for off in (-F, F):
                dline(WX0 + off, WY0 + off, WX1 - off, WY0 + off)
                dline(WX0 + off, WY1 - off, WX1 - off, WY1 - off)
                dline(WX0 + off, WY0 + off, WX0 + off, WY1 - off)
                dline(WX1 - off, WY0 + off, WX1 - off, WY1 - off)
            note(WX0 + 1.0, WY0 - 2.6, '15" x 12" CONT. CONC. FOOTING W/ (2) #4 CONT.\nTOP & BOTTOM - TYP. AT ALL EXTERIOR WALLS')
            note(WX0 + 1.0, (WY0 + WY1) / 2.0, '4" MIN. CONC. SLAB ON GRADE OVER\n6 MIL VAPOR BARRIER OVER 4" SAND')
            note(WX0 + 1.0, WY1 + 2.2, 'FOUNDATION PER DETAIL ON SD1')
        elif kind in ('floor', 'roof'):
            SP = 1.3333 if kind == 'floor' else 2.0     # 16" o.c. joists / 24" o.c. trusses
            x = WX0 + SP
            n = 0
            while x < WX1 - 0.2:
                dline(x, WY0 + 0.35, x, WY1 - 0.35)
                x += SP; n += 1
            mid = (WX0 + WX1) / 2.0
            # span arrow across the members
            dline(WX0 + 1.0, WY0 + 3.0, WX1 - 1.0, WY0 + 3.0)
            if kind == 'floor':
                note(WX0 + 1.0, WY0 - 2.6, '2x10 D.F. #2 FLOOR JOISTS @ 16" O.C.\nSPAN AS SHOWN - SEE DETAIL ON SD1')
                note(mid - 6.0, WY1 + 2.2, 'BEARING WALL BELOW')
            else:
                note(WX0 + 1.0, WY0 - 2.6, 'PRE-ENGINEERED ROOF TRUSSES @ 24" O.C.\nPER TRUSS MFR. CALCS - 5:12 PITCH')
                note(mid - 6.0, WY1 + 2.2, 'RIDGE')
            L.append('%s: %d members @ %.2f ft o.c.' % (v.Name, n, SP))
    doc.Regenerate()
    # sheet ADU-8
    sh = None
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == 'ADU-8': sh = s; break
    if sh is None:
        sh = ViewSheet.Create(doc, TB); sh.SheetNumber = 'ADU-8'
    sh.Name = '4439 Keeler Ave ADU - Foundation & Framing'
    doc.Regenerate()
    xs = [0.55, 1.45, 2.35]
    for i, (v, kind) in enumerate(made_views):
        have = None
        for vp in FEC(doc, sh.Id).OfClass(Viewport):
            if vp.ViewId == v.Id: have = vp; break
        p = _XYZ(xs[i], 1.25, 0)
        if have: have.SetBoxCenter(p)
        elif Viewport.CanAddViewToSheet(doc, sh.Id, v.Id):
            vp = Viewport.Create(doc, sh.Id, v.Id, p)
            vp.LabelOffset = _XYZ(0, 0, 0)
        else:
            L.append('cannot place %s' % v.Name); continue
        L.append('placed %s at (%.2f, 1.25)' % (v.Name, xs[i]))
    doc.Regenerate(); t.Commit()
    result = '\n'.join(L)

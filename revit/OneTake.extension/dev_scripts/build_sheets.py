# Build a sheet set: duplicate source views, crop them to a region, create sheets, place views+legends.
# args {"titleblock":311500, "region":[x0,y0,x1,y1], "prefix":"ADU", "dry":true,
#       "sheets":[{"number":"ADU-1","name":"...",
#                  "views":[{"src":718579,"rename":"ADU - 1st Floor Plan","recrop":false,"at":[x,y]}],
#                  "legends":[{"src":1133721,"at":[x,y]}]}]}
from Autodesk.Revit.DB import (View, ViewSheet, Viewport, ViewDuplicateOption, BoundingBoxXYZ,
                               BuiltInParameter, ElementId as EId, TransactionGroup,
                               IFailuresPreprocessor, FailureProcessingResult, FailureSeverity)

class _Safe(IFailuresPreprocessor):
    def PreprocessFailures(self, fa):
        bad = False
        for f in fa.GetFailureMessages():
            if f.GetSeverity() == FailureSeverity.Warning: fa.DeleteWarning(f)
            else: bad = True
        return FailureProcessingResult.ProceedWithRollBack if bad else FailureProcessingResult.Continue

def safe_tx(n):
    t = Transaction(doc, n)
    o = t.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(_Safe()); o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o); return t

reg = args.get('region')
tb = EId(long(args['titleblock']))
out = []
existing = {}
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    existing[s.SheetNumber] = s
names = set()
for v in FilteredElementCollector(doc).OfClass(View):
    try: names.add(v.Name)
    except Exception: pass

def uniq_name(n):
    if n not in names:
        names.add(n); return n
    i = 2
    while '%s %d' % (n, i) in names: i += 1
    names.add('%s %d' % (n, i)); return '%s %d' % (n, i)

def recrop(v):
    if not reg: return
    bb = v.CropBox; tf = bb.Transform; inv = tf.Inverse
    pts = [inv.OfPoint(XYZ(float(reg[0]), float(reg[1]), 0)),
           inv.OfPoint(XYZ(float(reg[2]), float(reg[3]), 0))]
    xs = [p.X for p in pts]; ys = [p.Y for p in pts]
    nb = BoundingBoxXYZ(); nb.Transform = tf
    nb.Min = XYZ(min(xs), min(ys), bb.Min.Z); nb.Max = XYZ(max(xs), max(ys), bb.Max.Z)
    v.CropBox = nb; v.CropBoxActive = True; v.CropBoxVisible = False

if args.get('dry', True):
    for sd in args['sheets']:
        rec = {'sheet': sd['number'], 'name': sd['name'],
               'exists': sd['number'] in existing, 'views': [], 'legends': []}
        for vd in sd.get('views', []):
            src = doc.GetElement(EId(long(vd['src'])))
            rec['views'].append('%s -> %s%s' % (src.Name if src else '??', vd.get('rename', '?'),
                                                ' (recrop)' if vd.get('recrop') else ''))
        for ld in sd.get('legends', []):
            l = doc.GetElement(EId(long(ld['src'])))
            rec['legends'].append(l.Name if l else '??')
        out.append(rec)
    result = {'dry': True, 'plan': out}
else:
    tg = TransactionGroup(doc, 'OneTake: build sheet set'); tg.Start()
    t = safe_tx('sheets'); t.Start()
    try:
        for sd in args['sheets']:
            if sd['number'] in existing:
                out.append({'sheet': sd['number'], 'skipped': 'already exists'}); continue
            sh = ViewSheet.Create(doc, tb)
            sh.SheetNumber = sd['number']
            sh.Name = sd['name']
            doc.Regenerate()
            placed = []
            for vd in sd.get('views', []):
                src = doc.GetElement(EId(long(vd['src'])))
                nv = doc.GetElement(src.Duplicate(ViewDuplicateOption.WithDetailing))
                try: nv.Name = uniq_name(vd.get('rename') or (src.Name + ' - ADU'))
                except Exception: pass
                if vd.get('recrop'): recrop(nv)
                elif vd.get('cropon'):
                    nv.CropBoxActive = True; nv.CropBoxVisible = False
                doc.Regenerate()
                at = vd.get('at', [1.0, 1.0])
                vp = Viewport.Create(doc, sh.Id, nv.Id, XYZ(float(at[0]), float(at[1]), 0))
                placed.append({'view': nv.Name, 'id': nv.Id.Value, 'vp': vp.Id.Value if vp else None})
            for ld in sd.get('legends', []):
                at = ld.get('at', [2.4, 1.0])
                vp = Viewport.Create(doc, sh.Id, EId(long(ld['src'])), XYZ(float(at[0]), float(at[1]), 0))
                placed.append({'legend': doc.GetElement(EId(long(ld['src']))).Name,
                               'vp': vp.Id.Value if vp else None})
            doc.Regenerate()
            out.append({'sheet': sh.SheetNumber, 'name': sh.Name, 'id': sh.Id.Value, 'placed': placed})
        t.Commit(); tg.Assimilate()
    except Exception:
        try: t.RollBack()
        except Exception: pass
        tg.RollBack(); raise
    result = {'created': len([o for o in out if 'id' in o]), 'detail': out}

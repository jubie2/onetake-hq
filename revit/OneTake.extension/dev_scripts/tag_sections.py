# Add keynote tags + room names to section views.
# args {"views":["ADU - Section 1",...], "keynote_tag":117961, "room_tag":84095, "dry":true}
from Autodesk.Revit.DB import (View, FilteredElementCollector as FEC, BuiltInCategory, BuiltInParameter,
                               IndependentTag, TagMode, TagOrientation, Reference, XYZ as _XYZ,
                               LinkElementId, UV, TextNote, TextNoteOptions, ElementId as EId,
                               TransactionGroup, IFailuresPreprocessor, FailureProcessingResult,
                               FailureSeverity)
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

kn_tag = EId(long(args['keynote_tag'])); rm_tag = EId(long(args.get('room_tag', 0) or 0))
L = []
tg = None; t = None
if not args.get('dry', True):
    tg = TransactionGroup(doc, 'OneTake: tag sections'); tg.Start()
    t = safe_tx('tags'); t.Start()
try:
    for nm in args['views']:
        vs = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
        if not vs:
            L.append('%s: not found' % nm); continue
        v = vs[0]
        inv = v.CropBox.Transform.Inverse
        made_k, made_r, errs = 0, 0, []
        # ---- keynote tags: one per distinct keynote value in the view
        seen = set()
        for bic in (BuiltInCategory.OST_Roofs, BuiltInCategory.OST_Walls, BuiltInCategory.OST_Floors,
                    BuiltInCategory.OST_StructuralFoundation):
            for e in FEC(doc, v.Id).OfCategory(bic).WhereElementIsNotElementType():
                try:
                    ty = doc.GetElement(e.GetTypeId())
                    p = ty.get_Parameter(BuiltInParameter.KEYNOTE_PARAM) if ty else None
                    val = p.AsString() if p else None
                    if not val or val in seen: continue
                    bb = e.get_BoundingBox(v)
                    if bb is None: continue
                    c = (bb.Min + bb.Max) * 0.5
                    if not args.get('dry', True):
                        IndependentTag.Create(doc, kn_tag, v.Id, Reference(e), True,
                                              TagOrientation.Horizontal, c)
                        doc.Regenerate()
                    seen.add(val); made_k += 1
                except Exception as ex:
                    errs.append('kn:%s' % ex)
        # ---- room names
        for r in FEC(doc, v.Id).OfCategory(BuiltInCategory.OST_Rooms):
            try:
                nmr = r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() or ''
                bb = r.get_BoundingBox(v)
                if bb is None: continue
                c = (bb.Min + bb.Max) * 0.5
                if not args.get('dry', True):
                    placed = False
                    if rm_tag.Value != 0:
                        try:
                            loc = inv.OfPoint(c)
                            doc.Create.NewRoomTag(LinkElementId(r.Id), UV(loc.X, loc.Y), v.Id)
                            placed = True
                        except Exception as ex:
                            errs.append('roomtag:%s' % str(ex)[:40])
                    if not placed:
                        tnt = doc.GetDefaultElementTypeId(__import__('Autodesk').Revit.DB.ElementTypeGroup.TextNoteType)
                        TextNote.Create(doc, v.Id, c, nmr, tnt)
                    doc.Regenerate()
                made_r += 1
            except Exception as ex:
                errs.append('room:%s' % str(ex)[:40])
        L.append('%-22s keynote tags=%d  room labels=%d %s' %
                 (nm[:22], made_k, made_r, ('errs: ' + '; '.join(errs[:2])) if errs else ''))
    if not args.get('dry', True):
        doc.Regenerate(); t.Commit(); tg.Assimilate()
except Exception:
    if t is not None:
        try: t.RollBack()
        except Exception: pass
    if tg is not None: tg.RollBack()
    raise
result = '\n'.join(L)

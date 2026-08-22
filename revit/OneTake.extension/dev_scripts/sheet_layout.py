# Report or fix viewport placement on sheets. args {"sheets":["ADU-1",...], "dry":true,
#   "right_strip":1.3, "margin":0.15}
from Autodesk.Revit.DB import (ViewSheet, Viewport, BuiltInCategory, XYZ as _XYZ,
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

want = set(args.get('sheets', []))
STRIP = float(args.get('right_strip', 1.35))
M = float(args.get('margin', 0.12))
L = []
tg = None; t = None
if not args.get('dry', True):
    tg = TransactionGroup(doc, 'OneTake: sheet layout'); tg.Start()
    t = safe_tx('layout'); t.Start()
try:
    for sh in FilteredElementCollector(doc).OfClass(ViewSheet):
        if want and sh.SheetNumber not in want: continue
        tb = None
        for ti in FilteredElementCollector(doc, sh.Id).OfCategory(BuiltInCategory.OST_TitleBlocks):
            tb = ti.get_BoundingBox(sh)
        if tb is None:
            L.append('%s: no titleblock' % sh.SheetNumber); continue
        x0, y0, x1, y1 = tb.Min.X + M, tb.Min.Y + M, tb.Max.X - M, tb.Max.Y - M
        L.append('%s "%s"  sheet area x %.2f..%.2f  y %.2f..%.2f' % (sh.SheetNumber, sh.Name, x0, x1, y0, y1))
        vps, legs = [], []
        for vp in FilteredElementCollector(doc, sh.Id).OfClass(Viewport):
            v = doc.GetElement(vp.ViewId)
            o = vp.GetBoxOutline()
            w = o.MaximumPoint.X - o.MinimumPoint.X
            h = o.MaximumPoint.Y - o.MinimumPoint.Y
            try:                       # prefer the real drawing size (crop / scale)
                bb = v.CropBox
                if v.CropBoxActive and v.Scale:
                    w = (bb.Max.X - bb.Min.X) / float(v.Scale) + 0.16
                    h = (bb.Max.Y - bb.Min.Y) / float(v.Scale) + 0.16
                    if not args.get('dry', True):
                        try: vp.LabelLineLength = max(0.2, w - 0.1)
                        except Exception: pass
            except Exception:
                pass
            rec = (vp, v, w, h)
            (legs if str(v.ViewType) in ('Legend', 'DraftingView') else vps).append(rec)
        drawX1 = x1 - STRIP
        # views: pack into columns within (x0..drawX1, y0..y1), tallest first
        cx, cy, colw = x0, y1, 0.0
        for vp, v, w, h in sorted(vps, key=lambda r: -r[3]):
            if cy - h < y0 and cy != y1:
                cx += colw + 0.15; cy = y1; colw = 0.0
            px, py = cx + w/2.0, cy - h/2.0
            L.append('   view   %-30s %5.2f x %5.2f -> (%.2f, %.2f)' % (v.Name[:30], w, h, px, py))
            if not args.get('dry', True): vp.SetBoxCenter(_XYZ(px, py, 0))
            cy -= h + 0.12
            colw = max(colw, w)
        ly = y1
        for vp, v, w, h in legs:
            px, py = drawX1 + STRIP/2.0, ly - h/2.0
            L.append('   legend %-30s %5.2f x %5.2f -> (%.2f, %.2f)' % (v.Name[:30], w, h, px, py))
            if not args.get('dry', True): vp.SetBoxCenter(_XYZ(px, py, 0))
            ly -= h + 0.10
    if not args.get('dry', True):
        doc.Regenerate(); t.Commit(); tg.Assimilate()
except Exception:
    if t is not None:
        try: t.RollBack()
        except Exception: pass
    if tg is not None: tg.RollBack()
    raise
result = '\n'.join(L)

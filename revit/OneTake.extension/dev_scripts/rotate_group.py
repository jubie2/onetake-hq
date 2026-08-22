# Rotate + translate a set of elements as one group.
# args {"region":[x0,y0,x1,y1], "level":"1st Floor Level", "angle_deg":14.295,
#       "center":[x,y] (default = bbox centre of the selection), "dx":0, "dy":0, "dry":true}
from Autodesk.Revit.DB import (Wall, Line, ElementTransformUtils, TransactionGroup,
                               IFailuresPreprocessor, FailureProcessingResult, FailureSeverity)
from System.Collections.Generic import List
import math

class _Safe(IFailuresPreprocessor):
    def PreprocessFailures(self, fa):
        bad = False
        for f in fa.GetFailureMessages():
            if f.GetSeverity() == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            else:
                bad = True
        return FailureProcessingResult.ProceedWithRollBack if bad else FailureProcessingResult.Continue

def safe_tx(name):
    t = Transaction(doc, name)
    o = t.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(_Safe()); o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o)
    return t

reg = args['region']; lvl = args.get('level')
ids, xs, ys = [], [], []
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        c = w.Location.Curve
        p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
        if not all(reg[0] <= p.X <= reg[2] and reg[1] <= p.Y <= reg[3] for p in (p0, p1)):
            continue
        if lvl:
            l = doc.GetElement(w.LevelId)
            if l is None or l.Name != lvl:
                continue
        ids.append(w.Id); xs += [p0.X, p1.X]; ys += [p0.Y, p1.Y]
    except Exception:
        pass
if not ids:
    result = {'error': 'no walls in region'}
else:
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    cx, cy = args.get('center', [(bbox[0]+bbox[2])/2.0, (bbox[1]+bbox[3])/2.0])
    ang = math.radians(float(args.get('angle_deg', 0)))
    dx, dy = float(args.get('dx', 0)), float(args.get('dy', 0))
    if args.get('dry', True):
        # predict resulting bbox
        pts = []
        for x in (bbox[0], bbox[2]):
            for y in (bbox[1], bbox[3]):
                rx = cx + (x-cx)*math.cos(ang) - (y-cy)*math.sin(ang) + dx
                ry = cy + (x-cx)*math.sin(ang) + (y-cy)*math.cos(ang) + dy
                pts.append((rx, ry))
        nb = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
        result = {'walls': len(ids), 'bbox_now': [round(v,2) for v in bbox], 'centre': [round(cx,2), round(cy,2)],
                  'bbox_after': [round(v,2) for v in nb]}
    else:
        col = List[ElementId](ids)
        tg = TransactionGroup(doc, 'OneTake: rotate group'); tg.Start()
        t = safe_tx('rotate'); t.Start()
        axis = Line.CreateBound(XYZ(cx, cy, 0), XYZ(cx, cy, 10))
        ElementTransformUtils.RotateElements(doc, col, axis, ang)
        doc.Regenerate()
        if abs(dx) > 1e-9 or abs(dy) > 1e-9:
            ElementTransformUtils.MoveElements(doc, col, XYZ(dx, dy, 0))
            doc.Regenerate()
        t.Commit(); tg.Assimilate()
        xs2, ys2 = [], []
        for i in ids:
            c = doc.GetElement(i).Location.Curve
            for p in (c.GetEndPoint(0), c.GetEndPoint(1)):
                xs2.append(p.X); ys2.append(p.Y)
        result = {'walls': len(ids), 'rotated_deg': float(args.get('angle_deg', 0)),
                  'bbox_after': [round(min(xs2),2), round(min(ys2),2), round(max(xs2),2), round(max(ys2),2)]}

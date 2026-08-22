# Place windows/doors into traced openings.
# args {"level":"1st Floor Level", "dry":true,
#       "items":[{"x":..,"y":..,"w":3.0,"kind":"window|door|garage"}],
#       "sill":{"window":2.0}}
from Autodesk.Revit.DB import (FamilySymbol, Wall, Level, BuiltInParameter, StorageType,
                               TransactionGroup, IFailuresPreprocessor, FailureProcessingResult,
                               FailureSeverity, XYZ as _XYZ)
from Autodesk.Revit.DB.Structure import StructuralType
import re

class _Safe(IFailuresPreprocessor):
    def PreprocessFailures(self, fa):
        bad = False
        for f in fa.GetFailureMessages():
            if f.GetSeverity() == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            else:
                bad = True
        return FailureProcessingResult.ProceedWithRollBack if bad else FailureProcessingResult.Continue

def safe_tx(n):
    t = Transaction(doc, n)
    o = t.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(_Safe()); o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o); return t

PREF = {'window': r'Gliding|Casement|Picture|Fixed',
        'door':   r'Single|Flush|Panel|Twin',
        'garage': r'Garage|Overhead'}
CAT = {'window': 'Windows', 'door': 'Doors', 'garage': 'Doors'}

cands = {'Windows': [], 'Doors': []}
for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
    c = fs.Category.Name if fs.Category else ''
    if c not in cands: continue
    p = fs.LookupParameter('Width') or fs.LookupParameter('Rough Width')
    if p is None or p.StorageType != StorageType.Double: continue
    w = p.AsDouble()
    if w <= 0: continue
    cands[c].append((w, fs))

def pick(kind, want):
    pool = cands[CAT[kind]]
    rx = re.compile(PREF[kind], re.I)
    pref = [(abs(w-want), w, fs) for w, fs in pool if rx.search(fs.FamilyName)]
    use = pref or [(abs(w-want), w, fs) for w, fs in pool]
    if not use: return None, None
    use.sort(key=lambda t: t[0])
    return use[0][2], use[0][1]

level = [l for l in FilteredElementCollector(doc).OfClass(Level) if l.Name == args['level']][0]
wall_ids = []
for w in FilteredElementCollector(doc).OfClass(Wall):
    try:
        if doc.GetElement(w.LevelId).Name != args["level"]: continue
        if w.Location.Curve is None: continue
        wall_ids.append(w.Id)
    except Exception: pass

out, made = [], []
tg = None; t = None
if not args.get('dry', True):
    tg = TransactionGroup(doc, 'OneTake: openings'); tg.Start()
    t = safe_tx('place openings'); t.Start()
try:
    for it in args['items']:
        pt = _XYZ(float(it['x']), float(it['y']), level.Elevation)
        best, bd = None, 1e9
        for wid in wall_ids:
            try:
                w = doc.GetElement(wid)
                if w is None: continue
                c = w.Location.Curve
                if c is None: continue
                d = c.Distance(_XYZ(pt.X, pt.Y, c.GetEndPoint(0).Z))
            except Exception:
                continue
            if d < bd: best, bd = w, d
        sym, sw = pick(it['kind'], float(it['w']))
        rec = {'kind': it['kind'], 'want_w': round(float(it['w']), 2),
               'sym_w': round(sw, 2) if sw else None,
               'sym': (sym.FamilyName[:26] + ' : ' + (sym.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() or '')[:16]) if sym else None,
               'wall': best.Id.Value if best else None, 'dist': round(bd, 2)}
        if sym is None or best is None or bd > 2.5:
            rec['skip'] = 'no wall within 2.5 ft' if bd > 2.5 else 'no symbol'
            out.append(rec); continue
        if not args.get('dry', True):
            if not sym.IsActive:
                sym.Activate(); doc.Regenerate()
            p = best.Location.Curve.Project(_XYZ(pt.X, pt.Y, best.Location.Curve.GetEndPoint(0).Z)).XYZPoint
            inst = doc.Create.NewFamilyInstance(_XYZ(p.X, p.Y, level.Elevation), sym, best, level,
                                                StructuralType.NonStructural)
            doc.Regenerate()
            sh = it.get('sill')
            if sh is not None:
                q = inst.get_Parameter(BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                if q and not q.IsReadOnly: q.Set(float(sh))
            rec['id'] = inst.Id.Value
            made.append(inst.Id.Value)
        out.append(rec)
    if not args.get('dry', True):
        doc.Regenerate(); t.Commit(); tg.Assimilate()
except Exception:
    if t is not None:
        try: t.RollBack()
        except Exception: pass
    if tg is not None: tg.RollBack()
    raise
ok = [r for r in out if 'skip' not in r]
result = {'placed' if not args.get('dry', True) else 'would_place': len(ok),
          'skipped': len(out) - len(ok), 'sample': out[:14]}

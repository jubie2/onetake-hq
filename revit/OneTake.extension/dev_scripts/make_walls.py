# Create walls from a list in ONE transaction group. args:
# {"level":"1st Floor Level","height_ft":10,"walls":[{"type":"Generic - 5\"","a":[x,y],"b":[x,y]}]}
from Autodesk.Revit.DB import (Level, Wall, WallType, Line, BuiltInParameter,
                               TransactionGroup, FilteredElementCollector as FEC,
                               IFailuresPreprocessor, FailureProcessingResult, FailureSeverity)

class _Safe(IFailuresPreprocessor):
    """Delete warnings; ROLL BACK on errors (never silently resolve = never silently delete)."""
    def PreprocessFailures(self, fa):
        bad = False
        for f in fa.GetFailureMessages():
            if f.GetSeverity() == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            else:
                bad = True
        return FailureProcessingResult.ProceedWithRollBack if bad else FailureProcessingResult.Continue

def _safe_tx(name):
    t = Transaction(doc, name)
    o = t.GetFailureHandlingOptions()
    o.SetFailuresPreprocessor(_Safe())
    o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o)
    return t
level = [l for l in FEC(doc).OfClass(Level) if l.Name == args.get('level', '1st Floor Level')][0]
types = {}
for wt in FEC(doc).OfClass(WallType):
    n = wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    if n and n not in types:
        types[n] = wt
h = float(args.get('height_ft', 10))
made, errors = [], []
tg = TransactionGroup(doc, 'OneTake: make walls')
tg.Start()
t = Transaction(doc, 'walls'); _prep(t); t.Start()
try:
    for w in args['walls']:
        try:
            wt = types.get(w['type'])
            if wt is None:
                errors.append({'wall': w, 'error': 'no wall type ' + w['type']}); continue
            ln = Line.CreateBound(XYZ(float(w['a'][0]), float(w['a'][1]), level.Elevation),
                                  XYZ(float(w['b'][0]), float(w['b'][1]), level.Elevation))
            nw = Wall.Create(doc, ln, wt.Id, level.Id, h, 0.0, False, False)
            made.append({'id': nw.Id.Value, 'type': w['type'], 'a': w['a'], 'b': w['b']})
        except Exception as ex:
            errors.append({'wall': w, 'error': str(ex)})
    doc.Regenerate()
    t.Commit(); tg.Assimilate()
except Exception:
    t.RollBack(); tg.RollBack(); raise
# read back actual geometry + full wall id list for diffing
for m in made:
    c = doc.GetElement(ElementId(long(m['id']))).Location.Curve
    m['actual'] = [round(c.GetEndPoint(0).X, 2), round(c.GetEndPoint(0).Y, 2),
                   round(c.GetEndPoint(1).X, 2), round(c.GetEndPoint(1).Y, 2)]
all_ids = sorted(w.Id.Value for w in FEC(doc).OfClass(Wall))
result = {'made': made, 'errors': errors, 'wall_count': len(all_ids)}

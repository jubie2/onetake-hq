# Restore equipment instances + their Item params + tags, in ONE transaction group.
# Uses a SAFE failure handler: deletes warnings, ROLLS BACK on errors (never silently resolves).
from Autodesk.Revit.DB import (Level, FamilySymbol, BuiltInParameter, TransactionGroup, View,
                               IFailuresPreprocessor, FailureProcessingResult, FailureSeverity,
                               IndependentTag, TagMode, TagOrientation, Reference, StorageType)
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB import FailureHandlingOptions

class Safe(IFailuresPreprocessor):
    def __init__(self): self.errors = []
    def PreprocessFailures(self, fa):
        rolled = False
        for f in fa.GetFailureMessages():
            if f.GetSeverity() == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            else:
                self.errors.append(f.GetDescriptionText())
                rolled = True
        return FailureProcessingResult.ProceedWithRollBack if rolled else FailureProcessingResult.Continue

def safe_tx(name):
    t = Transaction(doc, name)
    o = t.GetFailureHandlingOptions()
    o.SetFailuresPreprocessor(Safe())
    o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o)
    return t

level = [l for l in FilteredElementCollector(doc).OfClass(Level) if l.Name == '1st Floor Level'][0]
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == args.get('view','Proposed Floor Plan')][0]
out = []
tg = TransactionGroup(doc, 'OneTake: restore items'); tg.Start()
t = safe_tx('place')
t.Start()
try:
    for it in args['items']:
        sym = doc.GetElement(ElementId(long(it['symbol'])))
        if not sym.IsActive:
            sym.Activate(); doc.Regenerate()
        pt = XYZ(float(it['x']), float(it['y']), level.Elevation)
        host = doc.GetElement(ElementId(long(it['host']))) if it.get('host') else None
        if host is not None:
            inst = doc.Create.NewFamilyInstance(pt, sym, host, level, StructuralType.NonStructural)
        else:
            inst = doc.Create.NewFamilyInstance(pt, sym, level, StructuralType.NonStructural)
        doc.Regenerate()
        if it.get('rotate'):
            from Autodesk.Revit.DB import Line, ElementTransformUtils
            import math
            c = inst.Location.Point
            ElementTransformUtils.RotateElement(doc, inst.Id, Line.CreateBound(c, c + XYZ.BasisZ), math.radians(float(it['rotate'])))
            doc.Regenerate()
        warn = []
        for k, v in (it.get('params') or {}).items():
            p = inst.LookupParameter(k)
            if p is None or p.IsReadOnly:
                warn.append(k); continue
            if p.StorageType == StorageType.String: p.Set(str(v))
            elif p.StorageType == StorageType.Double: p.Set(float(v))
            elif p.StorageType == StorageType.Integer: p.Set(int(v))
        doc.Regenerate()
        bb = inst.get_BoundingBox(None)
        rec = {'item': it.get('item'), 'id': inst.Id.Value, 'missing_params': warn,
               'bbox': [round(bb.Min.X,2), round(bb.Min.Y,2), round(bb.Max.X,2), round(bb.Max.Y,2)] if bb else None}
        if it.get('tag'):
            tag = IndependentTag.Create(doc, ElementId(long(it['tag'])), view.Id, Reference(inst), False,
                                        TagOrientation.Horizontal, XYZ(pt.X, pt.Y + float(it.get('tag_dy', 1.0)), pt.Z))
            doc.Regenerate()
            rec['tag_id'] = tag.Id.Value
            try: rec['tag_text'] = tag.TagText
            except Exception: pass
        out.append(rec)
    t.Commit()
    tg.Assimilate()
except Exception as ex:
    try: t.RollBack()
    except Exception: pass
    tg.RollBack()
    raise
result = out

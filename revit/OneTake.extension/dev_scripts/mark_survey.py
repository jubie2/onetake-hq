# All door/window marks in the doc, flag ones in the ranges we want to assign.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
want = set(['%03d' % n for n in range(101, 111)] + [str(n) for n in range(101, 111)]
           + ['%03d' % n for n in range(201, 211)] + [str(n) for n in range(201, 211)]
           + ['%02d' % n for n in range(1, 9)] + [str(n) for n in range(21, 29)])
L = []
for bic, lab in ((BIC.OST_Doors, 'DOOR'), (BIC.OST_Windows, 'WIN')):
    marks = {}
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        p = e.get_Parameter(BIP.ALL_MODEL_MARK)
        m = p.AsString() if p else None
        if m: marks.setdefault(m, []).append(e.Id.Value)
    clash = sorted(m for m in marks if m in want)
    L.append('%s: %d marked, clashes with target ranges: %s' % (lab, len(marks), clash or 'NONE'))
result = '\n'.join(L)

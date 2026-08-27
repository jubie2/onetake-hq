# Replace drawn SD/CO circles+labels with instances of the office 'Smoke' family
# (types: Smoke Detector / CARBONMONOXIDE). Both mech floors.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               CurveElement, FamilySymbol, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from System.Collections.Generic import List
SPOTS = [  # (x, y, 'SD'|'CO')
 (1164.2, -143.0, 'SD'),
 (1165.5, -132.6, 'SD'),
 (1167.8, -138.6, 'SD'),
 (1167.8, -140.5, 'CO'),
]
sd = co = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'Smoke':
        tn = s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        if 'CARBON' in tn.upper(): co = s
        else: sd = s
L = ['SD sym %s, CO sym %s' % (sd.Id.Value if sd else None, co.Id.Value if co else None)]
plans = {}
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    kill = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            if isinstance(e, CurveElement):
                m = e.GeometryCurve.Evaluate(0.5, True)
                if any(abs(m.X - p[0]) < 0.8 and abs(m.Y - p[1]) < 0.8 for p in SPOTS) \
                   and e.GeometryCurve.Length < 2.7:
                    kill.append(e.Id)
            elif isinstance(e, TextNote):
                if (e.Text or '').strip() in ('SD', 'CO'):
                    p0 = e.Coord
                    if any(abs(p0.X - p[0]) < 1.4 and abs(p0.Y - p[1]) < 1.4 for p in SPOTS):
                        kill.append(e.Id)
        except Exception: pass
    plans[nm] = (v, kill)
t = Transaction(doc, 'OneTake: SD/CO family'); _prep(t); t.Start()
for s in (sd, co):
    if s is not None and not s.IsActive:
        s.Activate()
doc.Regenerate()
for nm, (v, kill) in plans.items():
    if kill: doc.Delete(List[ElementId](kill))
    n = 0
    for x, y, kind in SPOTS:
        sym = sd if kind == 'SD' else co
        doc.Create.NewFamilyInstance(_XYZ(x, y, 0), sym, v)
        n += 1
    L.append('%s: wiped %d drawn, placed %d family instances' % (nm, len(kill), n))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

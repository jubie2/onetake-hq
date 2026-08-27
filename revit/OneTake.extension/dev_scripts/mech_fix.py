# Rebuild MECHANICAL KEYNOTES legend with numbered items (TAG LABEL circles),
# and delete the off-crop orphan symbol curves in the two mech plan views.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               TextNoteOptions, CurveElement, FamilySymbol,
                               HorizontalTextAlignment, BuiltInCategory as BIC,
                               ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
dry = args.get('dry', True)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
ITEMS = [
 "THERMOSTAT MOUNTED AT 5'-0\"",
 '6"x12" CEILING DIFFUSER',
 '6"x12" WALL DIFFUSER',
 'CEILING EXHAUST FAN (MIN. OF 75CFM) MIN. OF 4" DIA. DUCTED TO OUTSIDE',
 '4" DIA. DRYER EXHAUST DUCT TO OUTSIDE - TWO 90 DEG. ELBOWS MAX., 14\' MAX. LENGTH',
 'DRYER EXHAUST DUCT TERMINATION LOCATION',
 'KITCHEN HOOD EXHAUST FAN (SEE SCHEDULE) MIN. OF 250CFM FOR INTERMITTENT',
 '6" DIA. KITCHEN EXHAUST DUCT TO OUTSIDE BLDG',
 'KITCHEN EXHAUST DUCT TERMINATION LOCATION (PROVIDE W/ RAIN CAP)',
 'WATER HEATER P&T LINE TO OUTSIDE BLDG',
 'WATER HEATER FLUE VENT TO OUTSIDE BLDG (UP TO ROOF)',
 'ATTIC ACCESS LOCATION MIN. OF 22"x30" (MIN. 30"x30" IF EQUIPMENT REQUIRES)',
 '24"x24" REGISTER AIR RETURN GRILLE',
 'FAU-1 LOCATION IN CEILING ATTIC',
 'IAQ EF FAN 64CFM',
]
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
lg = getview('MECHANICAL KEYNOTES')
old1 = doc.GetElement(ElementId(1183395))
ttid = old1.GetTypeId()
sym = None
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if s.Family.Name == 'TAG LABEL': sym = s; break
L = ['legend scale %s, texttype %s' % (lg.Scale, ttid.Value)]
# orphan curves outside the crop region in the mech plan views
kill = []
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = getview(nm)
    n = 0
    for e in FEC(doc, v.Id).OfClass(CurveElement):
        try:
            m = e.GeometryCurve.Evaluate(0.5, True)
            if not (X0 <= m.X <= X1 and Y0 <= m.Y <= Y1):
                kill.append(e.Id); n += 1
        except Exception: pass
    L.append('%s: %d orphan curves' % (nm, n))
if not dry:
    t = Transaction(doc, 'OneTake: mech legend + cleanup'); _prep(t); t.Start()
    doc.Delete(List[ElementId]([ElementId(1183395), ElementId(1892507)]))
    if kill: doc.Delete(List[ElementId](kill))
    if not sym.IsActive:
        sym.Activate(); doc.Regenerate()
    o = TextNoteOptions(ttid)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    made = []
    for i, txt in enumerate(ITEMS):
        col = 0 if i < 8 else 1
        row = i if i < 8 else i - 8
        x = 6.35 if col == 0 else 11.15
        y = 39.45 - row * 0.62
        tn = TextNote.Create(doc, lg.Id, _XYZ(x, y, 0), 3.6, txt, o)
        fi = doc.Create.NewFamilyInstance(_XYZ(x - 0.42, y - 0.10, 0), sym, lg)
        made.append((fi.Id, str(i + 1)))
    doc.Regenerate()
    for eid, num in made:
        p = doc.GetElement(eid).LookupParameter('TEXT')
        if p and p.AsString() != num: p.Set(num)
    doc.Regenerate(); t.Commit()
    bad = [num for eid, num in made
           if doc.GetElement(eid).LookupParameter('TEXT').AsString() != num]
    L.append('legend rebuilt, 15 items%s' % (', BAD ' + ','.join(bad) if bad else ' verified'))
result = '\n'.join(L)

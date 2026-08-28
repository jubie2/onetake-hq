# Which plan views contain TAG LABELs / room tags, and what's on A200/A201?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, BuiltInCategory as BIC, ViewType)
L = []
NAMES = ['1st Floor Plan', '2nd FLoor Level', 'ADU 1st Floor Mech Plan',
         'ADU 2nd Floor Mech Plan', 'ADU 1st Floor Elec Plan', 'ADU 2nd Floor Elec Plan']
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or v.Name not in NAMES: continue
    ntag = 0
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'TAG LABEL': ntag += 1
        except Exception: pass
    nrm = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_RoomTags).WhereElementIsNotElementType()))
    nel = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType()))
    nlt = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType()))
    L.append('%s (id %s): tags=%d roomtags=%d elec=%d light=%d' % (
        v.Name, v.Id.Value, ntag, nrm, nel, nlt))
for sn in ['A200', 'A201']:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sn:
            vv = [doc.GetElement(vp.ViewId).Name for vp in FEC(doc, s.Id).OfClass(Viewport)]
            L.append('%s: %s' % (sn, vv))
result = '\n'.join(L)

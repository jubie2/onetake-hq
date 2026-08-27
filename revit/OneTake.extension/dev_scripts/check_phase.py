# Compare phases: views vs register elements.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInParameter as BIP)
L = []
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    p = v.get_Parameter(BIP.VIEW_PHASE)
    ph = doc.GetElement(p.AsElementId()) if p else None
    L.append('%s phase: %s' % (nm, ph.Name if ph else '?'))
for eid in (2186781, 2196380):
    e = doc.GetElement(ElementId(eid))
    pc = e.get_Parameter(BIP.PHASE_CREATED)
    ph = doc.GetElement(pc.AsElementId()) if pc else None
    lvl = e.get_Parameter(BIP.FAMILY_LEVEL_PARAM)
    lv = doc.GetElement(lvl.AsElementId()) if lvl else None
    L.append('elem %s phase %s level %s' % (eid, ph.Name if ph else '?',
                                            lv.Name if lv else '?'))
result = '\n'.join(L)

# Why doesn't the 2nd floor mech view show mech equipment? args {}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInCategory as BIC, PlanViewPlane)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - 2nd Floor Mechanical Plan': v = x; break
L = ['view id %s template %s' % (v.Id.Value, v.ViewTemplateId.Value)]
cid = ElementId(BIC.OST_MechanicalEquipment)
try: L.append('MechEq hidden in view: %s' % v.GetCategoryHidden(cid))
except Exception as ex: L.append('cat check fail %s' % str(ex)[:50])
try:
    vr = v.GetViewRange()
    for pl, nm in ((PlanViewPlane.TopClipPlane, 'top'), (PlanViewPlane.CutPlane, 'cut'),
                   (PlanViewPlane.BottomClipPlane, 'bottom'), (PlanViewPlane.ViewDepthPlane, 'depth')):
        lid = vr.GetLevelId(pl)
        off = vr.GetOffset(pl)
        lvl = doc.GetElement(lid)
        L.append('%s: %s + %.2f' % (nm, lvl.Name if lvl else lid.Value, off))
except Exception as ex:
    L.append('range fail %s' % str(ex)[:60])
n = 0
for e in FEC(doc, v.Id).OfCategory(BIC.OST_MechanicalEquipment).WhereElementIsNotElementType():
    n += 1
L.append('collector sees %d mech equipment' % n)
result = '\n'.join(L)

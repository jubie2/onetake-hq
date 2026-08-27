# Set the copied registers' Phase Created to New Construction; delete the five
# attic-stranded originals; verify visibility in the 2nd floor mech view.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInParameter as BIP, BuiltInCategory as BIC)
from System.Collections.Generic import List
src = doc.GetElement(ElementId(2186781))
phid = src.get_Parameter(BIP.PHASE_CREATED).AsElementId()
t = Transaction(doc, 'OneTake: register phase'); _prep(t); t.Start()
for i in (2196380, 2196381, 2196382, 2196383, 2196384):
    e = doc.GetElement(ElementId(i))
    e.get_Parameter(BIP.PHASE_CREATED).Set(phid)
doc.Delete(List[ElementId]([ElementId(i) for i in
                            (2186786, 2186787, 2186788, 2186789, 2186790)]))
doc.Regenerate(); t.Commit()
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'ADU - 2nd Floor Mechanical Plan': v = x; break
n = sum(1 for _ in FEC(doc, v.Id).OfCategory(BIC.OST_MechanicalEquipment)
        .WhereElementIsNotElementType())
result = 'phases fixed, attic strays deleted, %d registers now visible on 2nd' % n

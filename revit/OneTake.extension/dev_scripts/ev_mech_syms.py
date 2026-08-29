# Symbols available for mechanical devices (no Rooms collector - it crashes this model).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
CATS = [('MechEquip', BIC.OST_MechanicalEquipment), ('AirTerminal', BIC.OST_DuctTerminal),
        ('FireAlarm', BIC.OST_FireAlarmDevices), ('CommDevice', BIC.OST_CommunicationDevices),
        ('SecurityDev', BIC.OST_SecurityDevices), ('NurseCall', BIC.OST_NurseCallDevices),
        ('ElecFixture', BIC.OST_ElectricalFixtures), ('ElecEquip', BIC.OST_ElectricalEquipment),
        ('GenericModel', BIC.OST_GenericModel), ('SpecEquip', BIC.OST_SpecialityEquipment),
        ('PlumbFixture', BIC.OST_PlumbingFixtures), ('GenericAnno', BIC.OST_GenericAnnotation)]
KEY = ('smoke', 'carbon', 'monox', 'detect', 'alarm', 'fan', 'exhaust', 'split', 'ac ',
       'condens', 'heat', 'water heater', 'thermo', 'vent', 'grille', 'register',
       'diffuser', 'louver', 'dryer', 'hood', 'wh')
L = []
for name, cat in CATS:
    hits = []
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(cat):
        fam = s.Family.Name
        typ = s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        low = (fam + ' ' + typ).lower()
        if any(k in low for k in KEY):
            hits.append('%s :: %s  [id %s]' % (fam, typ, s.Id.Value))
    if hits:
        L.append('--- %s ---' % name)
        for h in sorted(set(hits)): L.append('  ' + h)
result = '\n'.join(L) or 'no matching symbols'

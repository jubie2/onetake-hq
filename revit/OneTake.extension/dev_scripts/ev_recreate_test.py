# Wall 2189148 is currently flipped. Re-create one of its devices and see whether the
# new instance picks up the reversed wall normal (i.e. faces into the room).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
e = doc.GetElement(ElementId(2244840))
p = e.Location.Point; sym = e.Symbol; h = e.Host
lvl = doc.GetElement(e.LevelId)
zoff = e.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM).AsDouble()
ph = e.get_Parameter(BIP.PHASE_CREATED).AsElementId()
L = ['wall orientation now (%.3f,%.3f)' % (h.Orientation.X, h.Orientation.Y),
     'old device facing (%.2f,%.2f)' % (e.FacingOrientation.X, e.FacingOrientation.Y)]
t = Transaction(doc, 'OneTake: recreate on flipped wall'); _prep(t); t.Start()
doc.Delete(e.Id); doc.Regenerate()
fi = doc.Create.NewFamilyInstance(_XYZ(p.X, p.Y, p.Z), sym, h, lvl,
                                  StructuralType.NonStructural)
doc.Regenerate()
pe = fi.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
if pe and not pe.IsReadOnly: pe.Set(zoff)
try: fi.get_Parameter(BIP.PHASE_CREATED).Set(ph)
except Exception: pass
doc.Regenerate()
L.append('new device %s facing (%.2f,%.2f)  loc (%.2f,%.2f)' % (
    fi.Id.Value, fi.FacingOrientation.X, fi.FacingOrientation.Y,
    fi.Location.Point.X, fi.Location.Point.Y))
t.Commit()
result = '\n'.join(L)

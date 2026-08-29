# Reverse wall 2189148's location curve, then re-create its devices: does the new
# instance face the other way? (Windows/doors in the wall are reported for damage check.)
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               Line, BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Structure import StructuralType
w = doc.GetElement(ElementId(2189148))
c = w.Location.Curve
a0 = c.GetEndPoint(0); b0 = c.GetEndPoint(1)
L = ['curve before (%.2f,%.2f)->(%.2f,%.2f)  orientation (%.3f,%.3f)' % (
    a0.X, a0.Y, b0.X, b0.Y, w.Orientation.X, w.Orientation.Y)]
ins = list(w.FindInserts(True, True, True, True))
for i in ins:
    el = doc.GetElement(i)
    try:
        L.append('  insert %s %s facing(%.2f,%.2f) hand(%.2f,%.2f)' % (
            i.Value, el.Category.Name, el.FacingOrientation.X, el.FacingOrientation.Y,
            el.HandOrientation.X, el.HandOrientation.Y))
    except Exception: pass
dev = None
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try:
        if e.Host and e.Host.Id.Value == 2189148: dev = e; break
    except Exception: pass
t = Transaction(doc, 'OneTake: reverse wall curve'); _prep(t); t.Start()
try:
    w.Location.Curve = Line.CreateBound(b0, a0)
    doc.Regenerate()
    c2 = w.Location.Curve
    L.append('curve after  (%.2f,%.2f)->(%.2f,%.2f)  orientation (%.3f,%.3f)' % (
        c2.GetEndPoint(0).X, c2.GetEndPoint(0).Y, c2.GetEndPoint(1).X, c2.GetEndPoint(1).Y,
        w.Orientation.X, w.Orientation.Y))
    if dev is not None:
        d2 = doc.GetElement(dev.Id)
        if d2 is not None:
            L.append('existing device facing (%.2f,%.2f)' % (
                d2.FacingOrientation.X, d2.FacingOrientation.Y))
            p = d2.Location.Point; sym = d2.Symbol
            lvl = doc.GetElement(d2.LevelId)
            zoff = d2.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM).AsDouble()
            doc.Delete(d2.Id); doc.Regenerate()
            fi = doc.Create.NewFamilyInstance(_XYZ(p.X, p.Y, p.Z), sym, w, lvl,
                                              StructuralType.NonStructural)
            doc.Regenerate()
            pe = fi.get_Parameter(BIP.INSTANCE_ELEVATION_PARAM)
            if pe and not pe.IsReadOnly: pe.Set(zoff)
            doc.Regenerate()
            L.append('RECREATED device facing (%.2f,%.2f)' % (
                fi.FacingOrientation.X, fi.FacingOrientation.Y))
except Exception as ex:
    L.append('FAILED %s' % str(ex)[:80])
doc.Regenerate(); t.Commit()
result = '\n'.join(L)

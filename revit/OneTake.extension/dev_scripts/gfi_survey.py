# Survey receptacles + GFI labels in the kitchen zone of the electrical plans.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilyInstance,
                               TextNote, XYZ as _XYZ)
KX0, KX1, KY0, KY1 = 1172.0, 1188.0, -137.0, -124.0   # kitchen zone
L = []
for nm in ('ADU - 1st Floor Electrical Plan', 'ADU - 2nd Floor Electrical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    L.append('--- %s ---' % nm)
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            if isinstance(e, FamilyInstance):
                b = e.get_BoundingBox(v)
                if b is None: continue
                c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, 0)
                if not (KX0 <= c.X <= KX1 and KY0 <= c.Y <= KY1): continue
                fn = e.Symbol.Family.Name
                if e.Category and e.Category.Name in ('Electrical Fixtures',
                                                      'Generic Annotations',
                                                      'Lighting Devices', 'Lighting Fixtures'):
                    L.append('%s [%s] id %s (%.1f,%.1f)' % (
                        e.Category.Name[:12], fn[:28], e.Id.Value, c.X, c.Y))
            elif isinstance(e, TextNote):
                p = e.Coord
                if not (KX0 <= p.X <= KX1 and KY0 <= p.Y <= KY1): continue
                txt = (e.Text or '').replace('\r', ' ').strip()
                if len(txt) < 12:
                    L.append('TXT "%s" id %s (%.1f,%.1f)' % (txt, e.Id.Value, p.X, p.Y))
        except Exception: pass
result = '\n'.join(L)

# Report the current doc/view/crop context so we never guess.
from Autodesk.Revit.DB import (View, ViewPlan, Level, WallType, BuiltInParameter, ViewType,
                               FilteredElementCollector as FEC)
L = []
app = HOST_APP.uiapp.Application
L.append('OPEN DOCS:')
for d in app.Documents:
    try:
        L.append('  %-40s family=%s  %s' % (d.Title, d.IsFamilyDocument, d.PathName))
    except Exception: pass
uidoc = HOST_APP.uiapp.ActiveUIDocument
doc2 = uidoc.Document
L.append('ACTIVE DOC: %s' % doc2.Title)
v = doc2.ActiveView
L.append('ACTIVE VIEW: %s  type=%s  scale=1:%s  cropActive=%s' % (v.Name, v.ViewType, v.Scale, v.CropBoxActive))
try:
    lv = v.GenLevel
    L.append('  level: %s  elev=%.2f ft' % (lv.Name, lv.Elevation))
except Exception: pass
try:
    bb = v.CropBox; tf = bb.Transform
    p0 = tf.OfPoint(bb.Min); p1 = tf.OfPoint(bb.Max)
    L.append('  CROP (model ft): x %.2f..%.2f  y %.2f..%.2f   size %.2f x %.2f' %
             (min(p0.X,p1.X), max(p0.X,p1.X), min(p0.Y,p1.Y), max(p0.Y,p1.Y),
              abs(p1.X-p0.X), abs(p1.Y-p0.Y)))
except Exception as ex:
    L.append('  crop error %s' % ex)
L.append('LEVELS:')
for lv in sorted(FEC(doc2).OfClass(Level), key=lambda l: l.Elevation):
    L.append('  %-28s %8.2f ft' % (lv.Name, lv.Elevation))
L.append('WALL TYPES (first 25):')
for wt in list(FEC(doc2).OfClass(WallType))[:25]:
    n = wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    try: w = wt.Width * 12.0
    except Exception: w = 0
    L.append('  %-34s %.1f in' % (n, w))
L.append('PLAN VIEWS (name / crop):')
for pv in FEC(doc2).OfClass(ViewPlan):
    if pv.IsTemplate: continue
    L.append('  %-40s crop=%s' % (pv.Name, pv.CropBoxActive))
result = '\n'.join(L)

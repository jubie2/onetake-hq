# Are new-building walls in a design option? And do the new views have a template?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, ElementId,
                               DesignOption)
L = []
n = 0
for w in FEC(doc).OfClass(Wall):
    bb = w.get_BoundingBox(None)
    if bb and 1110 < (bb.Min.X + bb.Max.X) / 2 < 1210 and 55 < (bb.Min.Y + bb.Max.Y) / 2 < 135:
        do = w.DesignOption
        L.append('wall %s option=%s createdPhase=%s' % (
            w.Id.Value, do.Name if do else 'MAIN', w.CreatedPhaseId.Value))
        n += 1
        if n >= 5: break
for opt in FEC(doc).OfClass(DesignOption):
    L.append('OPTION %s "%s" primary=%s' % (opt.Id.Value, opt.Name, opt.IsPrimary))
for vid in [2244567, 718579]:
    v = doc.GetElement(ElementId(vid))
    L.append('view %s template=%s' % (v.Name, v.ViewTemplateId.Value))
result = '\n'.join(L)

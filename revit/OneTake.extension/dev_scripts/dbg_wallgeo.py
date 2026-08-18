from Autodesk.Revit.DB import Options, Line, Solid, ViewDetailLevel
w = doc.GetElement(ElementId(long(args.get('wall', 4977748))))
lc = w.Location.Curve
out = {'loc': [lc.GetEndPoint(0).ToString(), lc.GetEndPoint(1).ToString()], 'lines': []}
for withview in (False, True):
    opt = Options(); opt.ComputeReferences = True; opt.IncludeNonVisibleObjects = True
    if withview:
        from Autodesk.Revit.DB import View
        for v in FilteredElementCollector(doc).OfClass(View):
            if not v.IsTemplate and v.Name == 'Proposed Floor Plan':
                opt.View = v
    else:
        opt.DetailLevel = ViewDetailLevel.Fine
    for g in w.get_Geometry(opt):
        out['lines'].append({'withview': withview, 'type': g.GetType().Name,
                             'ref': (g.Reference is not None) if hasattr(g, 'Reference') else None,
                             'p': [g.GetEndPoint(0).ToString(), g.GetEndPoint(1).ToString()] if isinstance(g, Line) else None,
                             'dist': [round(lc.Distance(g.GetEndPoint(0)), 3), round(lc.Distance(g.GetEndPoint(1)), 3)] if isinstance(g, Line) else None})
result = out

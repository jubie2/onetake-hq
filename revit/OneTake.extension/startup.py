# -*- coding: utf-8 -*-
"""OneTake routes API — typed verb layer for driving Revit from Claude.

IronPython 2.7 ONLY. No f-strings, print is a statement.
Registered at pyRevit startup; edit -> RELOAD pyRevit -> curl to test.

Smoke test:
    curl http://localhost:48884/onetake-v1/status
"""
from pyrevit import routes, HOST_APP
from pyrevit import versionmgr

from Autodesk.Revit.DB import (
    Transaction,
    Level,
    Wall,
    WallType,
    Line,
    XYZ,
    FilteredElementCollector,
    BuiltInParameter,
    ElementId,
    FamilySymbol,
    Options,
    Solid,
    PlanarFace,
    ReferenceArray,
    ViewPlan,
    UV,
    LinkElementId,
    SketchPlane,
    Plane,
    CurveArray,
    ElementTransformUtils,
    LocationCurve,
    LocationPoint,
    StorageType,
    View,
    BuiltInCategory,
)
from Autodesk.Revit.DB.Structure import StructuralType
import math

api = routes.API('onetake-v1')

MM_TO_FT = 1.0 / 304.8


def _err(message, status=400):
    """JSON error the calling agent can actually read."""
    return routes.make_response(data={'ok': False, 'error': message}, status=status)


def _get_level(doc, name):
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == name:
            return lvl
    return None


def _get_wall_type(doc, name):
    for wt in FilteredElementCollector(doc).OfClass(WallType):
        if wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == name:
            return wt
    return None




# ── Failure handling: never let a warning dialog block the API ──
from Autodesk.Revit.DB import (IFailuresPreprocessor, FailureProcessingResult,
                               FailureSeverity)


class _SwallowWarnings(IFailuresPreprocessor):
    """Delete warnings; auto-resolve errors that offer a resolution."""
    def PreprocessFailures(self, fa):
        resolved = False
        for f in fa.GetFailureMessages():
            sev = f.GetSeverity()
            if sev == FailureSeverity.Warning:
                fa.DeleteWarning(f)
            elif f.HasResolutions():
                fa.ResolveFailure(f)
                resolved = True
        if resolved:
            return FailureProcessingResult.ProceedWithCommit
        return FailureProcessingResult.Continue


def _prep(t):
    """Attach the warning-swallowing preprocessor to a Transaction."""
    try:
        opts = t.GetFailureHandlingOptions()
        opts.SetFailuresPreprocessor(_SwallowWarnings())
        opts.SetClearAfterRollback(True)
        t.SetFailureHandlingOptions(opts)
    except Exception:
        pass

# ── Read-only verbs ──────────────────────────────────────────────

@api.route('/status', methods=['GET'])
def status():
    """Is the server alive, what are we attached to."""
    return {
        'ok': True,
        'revit_version': HOST_APP.version,
        'revit_build': HOST_APP.build,
        'pyrevit_version': versionmgr.get_pyrevit_version().get_formatted(),
    }


@api.route('/doc', methods=['GET'])
def doc_info(doc):
    """Active document + the levels and wall types verbs can target."""
    if doc is None:
        return _err('No active document. Open a project in Revit first.', 409)
    levels = [{'name': l.Name, 'elevation_ft': l.Elevation}
              for l in FilteredElementCollector(doc).OfClass(Level)]
    wall_types = [wt.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                  for wt in FilteredElementCollector(doc).OfClass(WallType)]
    return {
        'ok': True,
        'title': doc.Title,
        'levels': levels,
        'wall_types': wall_types,
    }


# ── Model-changing verbs ─────────────────────────────────────────

@api.route('/levels', methods=['POST'])
def create_level(doc, request):
    """Create a level.

    Body: {"name": "Level 3", "elevation_ft": 20.0}
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    name = data.get('name')
    elevation = data.get('elevation_ft')
    if not name or elevation is None:
        return _err('Required: name (str), elevation_ft (number).')
    if _get_level(doc, name):
        return _err('Level "{}" already exists.'.format(name), 409)

    t = Transaction(doc, 'OneTake: create level {}'.format(name))
    _prep(t)
    t.Start()
    try:
        lvl = Level.Create(doc, float(elevation))
        lvl.Name = name
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error: {}'.format(ex), 500)
    return {'ok': True, 'id': lvl.Id.Value, 'name': name, 'elevation_ft': float(elevation)}


@api.route('/walls', methods=['POST'])
def create_walls(doc, request):
    """Create walls along a polyline. ALL UNITS DECIMAL FEET.

    Body: {
        "points": [[0,0], [30,0], [30,20], [0,20]],   # feet, in order
        "closed": true,                                # join last -> first
        "level": "Level 1",
        "height_ft": 10.0,
        "wall_type": null                              # optional; doc default if null
    }
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    points = data.get('points')
    level_name = data.get('level')
    height = data.get('height_ft')
    if not points or len(points) < 2:
        return _err('Required: points, a list of at least 2 [x, y] pairs in FEET.')
    if not level_name or height is None:
        return _err('Required: level (str), height_ft (number).')

    level = _get_level(doc, level_name)
    if level is None:
        return _err('Level "{}" not found. GET /onetake-v1/doc lists levels.'.format(level_name), 404)

    wall_type_id = None
    type_name = data.get('wall_type')
    if type_name:
        wt = _get_wall_type(doc, type_name)
        if wt is None:
            return _err('WallType "{}" not found. GET /onetake-v1/doc lists types.'.format(type_name), 404)
        wall_type_id = wt.Id

    pts = [XYZ(float(p[0]), float(p[1]), 0.0) for p in points]
    pairs = zip(pts, pts[1:])
    if data.get('closed') and len(pts) > 2:
        pairs = pairs + [(pts[-1], pts[0])]

    created = []
    t = Transaction(doc, 'OneTake: create {} walls'.format(len(pairs)))
    _prep(t)
    t.Start()
    try:
        for start, end in pairs:
            if start.DistanceTo(end) < 0.01:  # degenerate segment, feet
                continue
            line = Line.CreateBound(start, end)
            if wall_type_id:
                # typed overload: works for Basic AND Curtain wall types
                wall = Wall.Create(doc, line, wall_type_id, level.Id,
                                   float(height), 0.0, False, False)
            else:
                wall = Wall.Create(doc, line, level.Id, False)
                hp = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
                if hp:
                    hp.Set(float(height))
            created.append(wall.Id.Value)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'wall_ids': created, 'count': len(created)}


@api.route('/delete', methods=['POST'])
def delete_elements(doc, request):
    """Delete elements by explicit ElementId list. One transaction; undoable.

    Body: {"ids": [4977585, 4977586]}
    Returns which ids were deleted (incl. dependents Revit removed) and
    which were not found. Refuses an empty list.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    ids = data.get('ids')
    if not ids or not isinstance(ids, list):
        return _err('Required: ids, a non-empty list of element ids.')

    found, missing = [], []
    for raw in ids:
        try:
            eid = ElementId(long(raw))
        except (ValueError, TypeError):
            return _err('Bad element id: {}'.format(raw))
        if doc.GetElement(eid) is None:
            missing.append(raw)
        else:
            found.append(eid)
    if not found:
        return _err('None of the ids exist in this document.', 404)

    deleted = []
    t = Transaction(doc, 'OneTake: delete {} elements'.format(len(found)))
    _prep(t)
    t.Start()
    try:
        for eid in found:
            for did in doc.Delete(eid):
                deleted.append(did.Value)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'deleted_ids': deleted, 'count': len(deleted),
            'not_found': missing}


# ── Helpers for annotation / placement verbs ─────────────────────

def _plan_view(doc, level, view_name=None):
    """A non-template floor plan for `level` (active view preferred)."""
    if view_name:
        for v in FilteredElementCollector(doc).OfClass(ViewPlan):
            if not v.IsTemplate and v.Name == view_name:
                return v
        return None
    av = doc.ActiveView
    if isinstance(av, ViewPlan) and not av.IsTemplate and \
            av.GenLevel is not None and av.GenLevel.Id == level.Id:
        return av
    for v in FilteredElementCollector(doc).OfClass(ViewPlan):
        if v.IsTemplate or v.GenLevel is None:
            continue
        if v.GenLevel.Id == level.Id and str(v.ViewType) == 'FloorPlan':
            return v
    return None


def _wall_line(wall):
    loc = wall.Location
    if not isinstance(loc, LocationCurve):
        return None
    return loc.Curve


def _planar_faces(wall):
    """[(normal XYZ, origin XYZ, Reference)] for every planar face."""
    opt = Options()
    opt.ComputeReferences = True
    opt.IncludeNonVisibleObjects = False
    out = []
    geo = wall.get_Geometry(opt)
    if geo is None:
        return out
    for g in geo:
        if isinstance(g, Solid):
            for f in g.Faces:
                if isinstance(f, PlanarFace) and f.Reference is not None:
                    out.append((f.FaceNormal, f.Origin, f.Reference))
    return out


def _fmt_ft(v):
    ft = int(math.floor(v))
    inch = (v - ft) * 12.0
    return "{}'-{:.1f}in".format(ft, inch)


# ── Read-only: walls readback ────────────────────────────────────

@api.route('/walls', methods=['GET'])
def list_walls(doc):
    """Every wall: id, type, level, start/end (ft), length (ft + ft-in)."""
    if doc is None:
        return _err('No active document.', 409)
    out = []
    for w in FilteredElementCollector(doc).OfClass(Wall):
        c = _wall_line(w)
        if c is None:
            continue
        p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
        lvl = doc.GetElement(w.LevelId)
        out.append({
            'id': w.Id.Value,
            'type': w.WallType.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(),
            'level': lvl.Name if lvl else None,
            'start': [round(p0.X, 3), round(p0.Y, 3)],
            'end': [round(p1.X, 3), round(p1.Y, 3)],
            'length_ft': round(c.Length, 3),
            'length_ftin': _fmt_ft(c.Length),
        })
    return {'ok': True, 'count': len(out), 'walls': out}


# ── Read-only: loaded family types ───────────────────────────────

@api.route('/families', methods=['GET'])
def list_families(doc, request):
    """Loaded FamilySymbols. Optional ?category=Doors (substring, case-insens)."""
    if doc is None:
        return _err('No active document.', 409)
    want = None
    try:
        want = (request.params or {}).get('category')
    except Exception:
        want = None
    out = []
    for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
        cat = fs.Category.Name if fs.Category else ''
        if want and want.lower() not in cat.lower():
            continue
        out.append({'id': fs.Id.Value, 'category': cat,
                    'family': fs.FamilyName,
                    'type': fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()})
    out.sort(key=lambda d: (d['category'], d['family'], d['type']))
    return {'ok': True, 'count': len(out), 'symbols': out}


@api.route('/load-family', methods=['POST'])
def load_family(doc, request):
    """Body: {"path": "C:/families/Range.rfa"} -> loads .rfa into the doc."""
    if doc is None:
        return _err('No active document.', 409)
    path = (request.data or {}).get('path')
    if not path:
        return _err('Required: path to an .rfa file.')
    t = Transaction(doc, 'OneTake: load family')
    _prep(t)
    t.Start()
    try:
        ok = doc.LoadFamily(path)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error: {}'.format(ex), 500)
    return {'ok': bool(ok), 'loaded': bool(ok), 'path': path}


# ── Place family instances (doors/windows hosted, or free-standing) ─

@api.route('/place', methods=['POST'])
def place_instances(doc, request):
    """Body: {"level": "1st Floor Level", "items": [
         {"symbol_id": 123, "x": 10, "y": 5, "rotation_deg": 90,
          "host_wall_id": 4977589,   # doors/windows; auto-nearest if omitted
          "label": "cashier"}]}   ALL UNITS FEET.
    Hosted categories (Doors/Windows) are snapped onto the host wall line.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    items = data.get('items') or []
    level = _get_level(doc, data.get('level') or '')
    if level is None or not items:
        return _err('Required: level (existing name), items (non-empty list).')

    walls = [w for w in FilteredElementCollector(doc).OfClass(Wall)
             if _wall_line(w) is not None]

    def nearest_wall(pt):
        best, bd = None, 1e9
        for w in walls:
            d = _wall_line(w).Distance(pt)
            if d < bd:
                best, bd = w, d
        return best, bd

    placed, errors = [], []
    t = Transaction(doc, 'OneTake: place {} instances'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for i, it in enumerate(items):
            try:
                sym = doc.GetElement(ElementId(long(it['symbol_id'])))
                if not isinstance(sym, FamilySymbol):
                    errors.append({'i': i, 'error': 'symbol_id is not a FamilySymbol'})
                    continue
                if not sym.IsActive:
                    sym.Activate()
                    doc.Regenerate()
                pt = XYZ(float(it['x']), float(it['y']), level.Elevation)
                cat = sym.Category.Name if sym.Category else ''
                hosted = cat in ('Doors', 'Windows') or it.get('host_wall_id')
                if hosted:
                    if it.get('host_wall_id'):
                        host = doc.GetElement(ElementId(long(it['host_wall_id'])))
                    else:
                        host, dist = nearest_wall(pt)
                        if host is None or dist > 3.0:
                            errors.append({'i': i, 'error': 'no wall within 3 ft to host'})
                            continue
                    pt = _wall_line(host).Project(pt).XYZPoint
                    pt = XYZ(pt.X, pt.Y, level.Elevation)
                    inst = doc.Create.NewFamilyInstance(pt, sym, host, level,
                                                        StructuralType.NonStructural)
                else:
                    inst = doc.Create.NewFamilyInstance(pt, sym, level,
                                                        StructuralType.NonStructural)
                    rot = float(it.get('rotation_deg') or 0)
                    if abs(rot) > 1e-6:
                        axis = Line.CreateBound(pt, pt + XYZ.BasisZ)
                        ElementTransformUtils.RotateElement(doc, inst.Id, axis,
                                                            math.radians(rot))
                placed.append({'i': i, 'id': inst.Id.Value,
                               'label': it.get('label'), 'category': cat})
            except Exception as ex:
                errors.append({'i': i, 'label': it.get('label'), 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'placed': placed, 'errors': errors,
            'count': len(placed)}


# ── Rooms + tags ────────────────────────────────────────────────

@api.route('/room-lines', methods=['POST'])
def room_lines(doc, request):
    """Room separation lines. Body: {"level": "...", "lines": [[[x1,y1],[x2,y2]], ...]}"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    lines = data.get('lines') or []
    if level is None or not lines:
        return _err('Required: level, lines (list of [[x1,y1],[x2,y2]]).')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    t = Transaction(doc, 'OneTake: room separation lines')
    _prep(t)
    t.Start()
    try:
        z = level.Elevation
        sp = SketchPlane.Create(doc, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ(0, 0, z)))
        ca = CurveArray()
        for a, b in lines:
            ca.Append(Line.CreateBound(XYZ(float(a[0]), float(a[1]), z),
                                       XYZ(float(b[0]), float(b[1]), z)))
        made = doc.Create.NewRoomBoundaryLines(sp, ca, view)
        ids = [e.Id.Value for e in made]
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'ids': ids, 'count': len(ids)}


@api.route('/rooms', methods=['POST'])
def create_rooms(doc, request):
    """Body: {"level": "...", "rooms": [{"name": "Kitchen", "x": 50, "y": 20}], "tag": true}"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    rooms = data.get('rooms') or []
    if level is None or not rooms:
        return _err('Required: level, rooms (non-empty list of {name,x,y}).')
    view = _plan_view(doc, level, data.get('view'))
    want_tag = data.get('tag', True)
    if want_tag and view is None:
        return _err('No floor plan view found for level (needed for tags).', 404)
    made, errors = [], []
    t = Transaction(doc, 'OneTake: create {} rooms'.format(len(rooms)))
    _prep(t)
    t.Start()
    try:
        for i, r in enumerate(rooms):
            try:
                uv = UV(float(r['x']), float(r['y']))
                room = doc.Create.NewRoom(level, uv)
                room.get_Parameter(BuiltInParameter.ROOM_NAME).Set(
                    str(r.get('name') or 'Room'))
                if r.get('number'):
                    room.get_Parameter(BuiltInParameter.ROOM_NUMBER).Set(
                        str(r['number']))
                tag_id = None
                if want_tag:
                    tag = doc.Create.NewRoomTag(LinkElementId(room.Id), uv, view.Id)
                    tag_id = tag.Id.Value
                made.append({'i': i, 'room_id': room.Id.Value, 'tag_id': tag_id,
                             'name': room.Name,
                             'area_sf': round(room.Area, 1)})
            except Exception as ex:
                errors.append({'i': i, 'name': r.get('name'), 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'rooms': made, 'errors': errors, 'count': len(made)}


# ── Dimensions ──────────────────────────────────────────────────

@api.route('/dimensions', methods=['POST'])
def create_dimensions(doc, request):
    """Linear dimensions in a plan view. ALL UNITS FEET.
    Body: {"level": "...", "view": null,
           "lengths":  [{"wall_id": 1, "offset_ft": 3.0}],          # wall end-to-end
           "between":  [{"wall_a": 1, "wall_b": 2, "axis": "x", "at": -4.0}]}
    offset_ft > 0 = left of the wall's draw direction.
    'between' measures the facing side-faces of two walls along axis x|y,
    with the dimension line at coordinate `at` on the other axis.
    """
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    if level is None:
        return _err('Required: level (existing name).')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    z = level.Elevation
    made, errors = [], []
    t = Transaction(doc, 'OneTake: dimensions')
    _prep(t)
    t.Start()
    try:
        for i, d in enumerate(data.get('lengths') or []):
            try:
                w = doc.GetElement(ElementId(long(d['wall_id'])))
                c = _wall_line(w)
                p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
                dirv = (p1 - p0).Normalize()
                side = XYZ(-dirv.Y, dirv.X, 0)
                cands = []
                for n, o, ref in _planar_faces(w):
                    if abs(n.Z) > 0.5 or abs(n.DotProduct(side)) > 0.95:
                        continue  # top/bottom or side faces
                    cands.append(((o - p0).DotProduct(dirv), ref))
                if len(cands) < 2:
                    errors.append({'i': i, 'wall_id': d['wall_id'],
                                   'error': 'end faces not found'})
                    continue
                cands.sort(key=lambda x: x[0])
                ra = ReferenceArray()
                ra.Append(cands[0][1])
                ra.Append(cands[-1][1])
                off = float(d.get('offset_ft', 3.0))
                a = XYZ(p0.X, p0.Y, z) + side * off
                b = XYZ(p1.X, p1.Y, z) + side * off
                dim = doc.Create.NewDimension(view, Line.CreateBound(a, b), ra)
                made.append({'i': i, 'id': dim.Id.Value, 'wall_id': d['wall_id'],
                             'value_ft': round(dim.Value, 3) if dim.Value else None})
            except Exception as ex:
                errors.append({'i': i, 'wall_id': d.get('wall_id'), 'error': str(ex)})

        for i, d in enumerate(data.get('between') or []):
            try:
                axis = XYZ.BasisX if str(d.get('axis', 'x')).lower() == 'x' else XYZ.BasisY
                wa = doc.GetElement(ElementId(long(d['wall_a'])))
                wb = doc.GetElement(ElementId(long(d['wall_b'])))
                ca_, cb_ = _wall_line(wa), _wall_line(wb)
                pa = ca_.Evaluate(0.5, True).DotProduct(axis)
                pb = cb_.Evaluate(0.5, True).DotProduct(axis)

                far = bool(d.get('far', False))

                def pick(w, toward):
                    best, bd = None, (-1.0 if far else 1e9)
                    for n, o, ref in _planar_faces(w):
                        if abs(n.DotProduct(axis)) < 0.99:
                            continue
                        dist = abs(o.DotProduct(axis) - toward)
                        better = (dist > bd) if far else (dist < bd)
                        if better:
                            best, bd = (o.DotProduct(axis), ref), dist
                    return best
                fa = pick(wa, pb)
                fb = pick(wb, pa)
                if fa is None or fb is None:
                    errors.append({'i': i, 'error': 'faces along axis not found'})
                    continue
                at = float(d.get('at', 0.0))
                if axis.X == 1:
                    a, b = XYZ(fa[0], at, z), XYZ(fb[0], at, z)
                else:
                    a, b = XYZ(at, fa[0], z), XYZ(at, fb[0], z)
                ra = ReferenceArray()
                ra.Append(fa[1])
                ra.Append(fb[1])
                dim = doc.Create.NewDimension(view, Line.CreateBound(a, b), ra)
                made.append({'i': i, 'id': dim.Id.Value, 'between': [d['wall_a'], d['wall_b']],
                             'value_ft': round(dim.Value, 3) if dim.Value else None})
            except Exception as ex:
                errors.append({'i': i, 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'dimensions': made, 'errors': errors, 'count': len(made)}


@api.route('/rooms', methods=['GET'])
def list_rooms(doc):
    """All rooms: id, name, number, level, area_sf."""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import BuiltInCategory
    out = []
    coll = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)
    for r in coll:
        try:
            lvl = doc.GetElement(r.LevelId) if r.LevelId else None
            out.append({'id': r.Id.Value,
                        'name': r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(),
                        'number': r.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString(),
                        'level': lvl.Name if lvl else None,
                        'area_sf': round(r.Area, 1)})
        except Exception as ex:
            out.append({'id': r.Id.Value, 'error': str(ex)})
    return {'ok': True, 'count': len(out), 'rooms': out}


@api.route('/room-tags', methods=['POST'])
def tag_rooms(doc, request):
    """Tag rooms that have no tag in the plan view.
    Body: {"level": "...", "view": null, "room_ids": [..] (optional; default all on level)}"""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import BuiltInCategory
    from Autodesk.Revit.DB.Architecture import RoomTag
    data = request.data or {}
    level = _get_level(doc, data.get('level') or '')
    if level is None:
        return _err('Required: level.')
    view = _plan_view(doc, level, data.get('view'))
    if view is None:
        return _err('No floor plan view found for level.', 404)
    tagged_rooms = set()
    for tg in FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_RoomTags):
        try:
            if tg.Room is not None:
                tagged_rooms.add(tg.Room.Id.Value)
        except Exception:
            pass
    want = data.get('room_ids')
    rooms = []
    for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms):
        if r.LevelId != level.Id or r.Area <= 0:
            continue
        if want and r.Id.Value not in [long(x) for x in want]:
            continue
        if r.Id.Value in tagged_rooms:
            continue
        rooms.append(r)
    made, errors = [], []
    t = Transaction(doc, 'OneTake: tag {} rooms'.format(len(rooms)))
    _prep(t)
    t.Start()
    try:
        for r in rooms:
            try:
                p = r.Location.Point
                uv = UV(p.X, p.Y)
                tag = doc.Create.NewRoomTag(LinkElementId(r.Id), uv, view.Id)
                made.append({'room_id': r.Id.Value, 'tag_id': tag.Id.Value,
                             'name': r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()})
            except Exception as ex:
                errors.append({'room_id': r.Id.Value, 'error': repr(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'tags': made, 'errors': errors, 'count': len(made),
            'view': view.Name, 'already_tagged': len(tagged_rooms)}


@api.route('/curtain-door', methods=['POST'])
def curtain_door(doc, request):
    """Swap the curtain panel nearest (x,y) on a curtain wall to a door/panel type.
    Body: {"wall_id": 123, "x": 50, "y": 0, "symbol_id": 4001162}  (feet)"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    try:
        wall = doc.GetElement(ElementId(long(data['wall_id'])))
        sym = doc.GetElement(ElementId(long(data['symbol_id'])))
        px, py = float(data['x']), float(data['y'])
    except Exception as ex:
        return _err('Required: wall_id, symbol_id, x, y. ({})'.format(ex))
    grid = getattr(wall, 'CurtainGrid', None)
    if grid is None:
        return _err('Wall {} is not a curtain wall.'.format(data['wall_id']))
    best, bd = None, 1e9
    if data.get("panel_id"):
        best, bd = doc.GetElement(ElementId(long(data["panel_id"]))), 0.0
    for pid in grid.GetPanelIds():
        p = doc.GetElement(pid)
        bb = p.get_BoundingBox(None)
        if bb is None:
            continue
        c = (bb.Min + bb.Max) * 0.5
        dist = XYZ(c.X, c.Y, 0).DistanceTo(XYZ(px, py, 0))
        if dist < bd:
            best, bd = p, dist
    if best is None:
        return _err('No panels found on wall.', 404)
    t = Transaction(doc, 'OneTake: curtain door')
    _prep(t)
    t.Start()
    try:
        if not sym.IsActive:
            sym.Activate()
            doc.Regenerate()
        best.Pinned = False
        try:
            best.ChangeTypeId(sym.Id)
        except Exception:
            best.Symbol = sym
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'panel_id': best.Id.Value, 'distance_ft': round(bd, 2),
            'new_type': sym.FamilyName}


# ── Parameters + schedules ───────────────────────────────────────

def _set_param(el, name, value):
    p = el.LookupParameter(name)
    if p is None:
        return 'no param "{}"'.format(name)
    if p.IsReadOnly:
        return 'param "{}" read-only'.format(name)
    try:
        st = str(p.StorageType)
        if st == 'String':
            p.Set(str(value))
        elif st == 'Double':
            p.Set(float(value))
        elif st == 'Integer':
            p.Set(int(value))
        elif st == 'ElementId':
            p.Set(ElementId(long(value)))
        else:
            return 'unsupported storage {}'.format(st)
    except Exception as ex:
        return 'set "{}" failed: {}'.format(name, ex)
    return None


@api.route('/set-params', methods=['POST'])
def set_params(doc, request):
    """Body: {"items": [{"id": 123,
                         "instance": {"Mark": "01", "Comments": "EXISTING"},
                         "type": {"Description": "...", "Manufacturer": "...", "Model": "..."},
                         "dup_type_name": "HS-1615W"   # optional: duplicate the symbol first
                       }]}"""
    if doc is None:
        return _err('No active document.', 409)
    items = (request.data or {}).get('items') or []
    if not items:
        return _err('Required: items (non-empty list).')
    results = []
    t = Transaction(doc, 'OneTake: set params on {} elements'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for it in items:
            res = {'id': it.get('id'), 'warnings': []}
            try:
                el = doc.GetElement(ElementId(long(it['id'])))
                if el is None:
                    res['warnings'].append('element not found')
                    results.append(res)
                    continue
                dup = it.get('dup_type_name')
                if dup and hasattr(el, 'Symbol'):
                    newsym = None
                    for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
                        if fs.FamilyName == el.Symbol.FamilyName and \
                                fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == dup:
                            newsym = fs
                            break
                    if newsym is None:
                        newsym = el.Symbol.Duplicate(dup)
                    if not newsym.IsActive:
                        newsym.Activate()
                    el.Symbol = newsym
                    res['type_id'] = newsym.Id.Value
                for k, v in (it.get('instance') or {}).items():
                    w = _set_param(el, k, v)
                    if w:
                        res['warnings'].append(w)
                tp = it.get('type') or {}
                if tp:
                    sym = getattr(el, 'Symbol', None) or doc.GetElement(el.GetTypeId())
                    for k, v in tp.items():
                        w = _set_param(sym, k, v)
                        if w:
                            res['warnings'].append('type: ' + w)
            except Exception as ex:
                res['warnings'].append(str(ex))
            results.append(res)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'results': results, 'count': len(results)}


def _schedule_rows(sched, max_rows=400):
    from Autodesk.Revit.DB import SectionType
    td = sched.GetTableData()
    rows = []
    for sec in (SectionType.Header, SectionType.Body):
        sd = td.GetSectionData(sec)
        if sd is None:
            continue
        for r in range(sd.NumberOfRows):
            row = []
            for c in range(sd.NumberOfColumns):
                try:
                    row.append(sched.GetCellText(sec, r, c))
                except Exception:
                    row.append('')
            rows.append(row)
            if len(rows) >= max_rows:
                return rows
    return rows


@api.route('/schedule', methods=['POST'])
def create_schedule(doc, request):
    """Create (or replace) a multi-category schedule.
    Body: {"name": "EQUIPMENT SCHEDULE",
           "fields": [{"param": "Mark", "heading": "ITEM"}, {"param": "Description"},
                      {"count": true, "heading": "QTY"}, {"param": "Manufacturer"},
                      {"param": "Model"}, {"param": "Comments", "heading": "STATUS"}],
           "filter": {"param": "Comments", "equals": "EXISTING"},
           "sort_by": "Mark", "itemize": false, "replace": true}
    param names: Mark, Description, Manufacturer, Model, Comments, Type Comments, Level, Family and Type..."""
    from Autodesk.Revit.DB import (ViewSchedule, BuiltInCategory, ScheduleFieldType,
                                   ScheduleFilter, ScheduleFilterType, ScheduleSortGroupField)
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    name = data.get('name') or 'OneTake Schedule'
    fields = data.get('fields') or []
    if not fields:
        return _err('Required: fields.')
    t = Transaction(doc, 'OneTake: schedule {}'.format(name))
    _prep(t)
    t.Start()
    try:
        if data.get('replace', False):
            # collect first: deleting while iterating invalidates the collector
            dup_ids = [v.Id for v in FilteredElementCollector(doc).OfClass(ViewSchedule)
                       if v.Name == name and not v.IsTemplate]
            for did in dup_ids:
                doc.Delete(did)
        cat = data.get('category')
        cat_id = ElementId(BuiltInCategory.INVALID)
        if cat:
            cat_id = ElementId(getattr(BuiltInCategory, cat))
        sched = ViewSchedule.CreateSchedule(doc, cat_id)
        sched.Name = name
        sdef = sched.Definition
        schedulable = list(sdef.GetSchedulableFields())
        by_name = {}
        count_sf = None
        for sf in schedulable:
            try:
                nm = sf.GetName(doc)
            except Exception:
                nm = None
            if sf.FieldType == ScheduleFieldType.Count:
                count_sf = sf
            if nm and nm not in by_name:
                by_name[nm] = sf
        added = {}
        missing = []
        for f in fields:
            if f.get('count'):
                sf = count_sf
            else:
                sf = by_name.get(f.get('param'))
            if sf is None:
                missing.append(f.get('param') or 'count')
                continue
            fld = sdef.AddField(sf)
            if f.get('heading'):
                fld.ColumnHeading = f['heading']
            if f.get('width_ft'):
                fld.GridColumnWidth = float(f['width_ft'])
            added[f.get('param') or 'count'] = fld
        flt = data.get('filter')
        if flt and flt.get('param') in added:
            sdef.AddFilter(ScheduleFilter(added[flt['param']].FieldId,
                                          ScheduleFilterType.Equal, str(flt['equals'])))
        sb = data.get('sort_by')
        if sb and sb in added:
            sdef.AddSortGroupField(ScheduleSortGroupField(added[sb].FieldId))
        sdef.IsItemized = bool(data.get('itemize', False))
        doc.Regenerate()
        rows = _schedule_rows(sched)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'schedule_id': sched.Id.Value, 'name': name,
            'missing_fields': missing, 'available_fields': sorted(by_name.keys())[:80],
            'rows': rows}


@api.route('/schedule-read', methods=['POST'])
def read_schedule(doc, request):
    """Body: {"name": "EQUIPMENT SCHEDULE"} -> header + body rows as text."""
    from Autodesk.Revit.DB import ViewSchedule
    if doc is None:
        return _err('No active document.', 409)
    name = (request.data or {}).get('name')
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.Name == name and not v.IsTemplate:
            return {'ok': True, 'schedule_id': v.Id.Value, 'rows': _schedule_rows(v)}
    return _err('Schedule "{}" not found.'.format(name), 404)


@api.route('/warnings', methods=['GET'])
def list_warnings(doc):
    """Model warnings (Manage > Warnings): description + failing element ids."""
    if doc is None:
        return _err('No active document.', 409)
    out = []
    for fm in doc.GetWarnings():
        try:
            out.append({'description': fm.GetDescriptionText(),
                        'severity': str(fm.GetSeverity()),
                        'element_ids': [e.Value for e in fm.GetFailingElements()],
                        'additional_ids': [e.Value for e in fm.GetAdditionalElements()]})
        except Exception as ex:
            out.append({'error': str(ex)})
    return {'ok': True, 'count': len(out), 'warnings': out}


# -- Schedule inspection / cloning, element info, tags -----------------------

def _pval(el, name):
    """String value of an instance param, falling back to the type param."""
    try:
        p = el.LookupParameter(name)
        if p is None and hasattr(el, 'Symbol') and el.Symbol is not None:
            p = el.Symbol.LookupParameter(name)
        if p is None:
            return "<no such param>"
        if p.StorageType == StorageType.String:
            return p.AsString()
        return p.AsValueString()
    except Exception:
        return None


def _schedule_info(doc, v, with_rows=3):
    from Autodesk.Revit.DB import ScheduleSheetInstance
    sdef = v.Definition
    fields = []
    for i in range(sdef.GetFieldCount()):
        f = sdef.GetField(i)
        try:
            pname = f.GetName()
        except Exception:
            pname = None
        fields.append({'index': i, 'heading': f.ColumnHeading, 'param': pname,
                       'type': str(f.FieldType), 'width_ft': f.GridColumnWidth,
                       'hidden': f.IsHidden,
                       'align': str(f.HorizontalAlignment)})
    filters = []
    for flt in sdef.GetFilters():
        try:
            fld = sdef.GetField(flt.FieldId)
            val = None
            if flt.IsStringValue:
                val = flt.GetStringValue()
            elif flt.IsDoubleValue:
                val = flt.GetDoubleValue()
            elif flt.IsIntegerValue:
                val = flt.GetIntegerValue()
            elif flt.IsElementIdValue:
                val = flt.GetElementIdValue().Value
            filters.append({'field': fld.ColumnHeading, 'type': str(flt.FilterType), 'value': val})
        except Exception as ex:
            filters.append({'error': str(ex)})
    sorts = []
    for sg in sdef.GetSortGroupFields():
        try:
            sorts.append({'field': sdef.GetField(sg.FieldId).ColumnHeading,
                          'order': str(sg.SortOrder), 'header': sg.ShowHeader,
                          'footer': sg.ShowFooter, 'blank_line': sg.ShowBlankLine})
        except Exception:
            pass
    placed = []
    for ssi in FilteredElementCollector(doc).OfClass(ScheduleSheetInstance):
        try:
            if ssi.ScheduleId == v.Id:
                owner = doc.GetElement(ssi.OwnerViewId)
                placed.append({'view_id': ssi.OwnerViewId.Value,
                               'view': owner.Name if owner else None,
                               'sheet_number': getattr(owner, 'SheetNumber', None),
                               'x': ssi.Point.X, 'y': ssi.Point.Y})
        except Exception:
            pass
    cat = None
    try:
        c = doc.Settings.Categories.get_Item(BuiltInCategory(sdef.CategoryId.Value))
        cat = c.Name if c else None
    except Exception:
        cat = None
    return {'id': v.Id.Value, 'name': v.Name, 'category_id': sdef.CategoryId.Value,
            'category': cat, 'itemized': sdef.IsItemized,
            'show_title': sdef.ShowTitle, 'show_headers': sdef.ShowHeaders,
            'fields': fields, 'filters': filters, 'sort': sorts,
            'placed_on': placed,
            'rows': _schedule_rows(v, with_rows) if with_rows else []}


@api.route('/schedules', methods=['GET'])
def list_schedules(doc, request):
    """All non-template schedules with columns, filters, sort, placement + first rows."""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import ViewSchedule
    out = []
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.IsTemplate or v.IsTitleblockRevisionSchedule:
            continue
        try:
            out.append(_schedule_info(doc, v, 4))
        except Exception as ex:
            out.append({'id': v.Id.Value, 'name': v.Name, 'error': str(ex)})
    out.sort(key=lambda d: d.get('name') or '')
    return {'ok': True, 'count': len(out), 'schedules': out}


@api.route('/schedule-clone', methods=['POST'])
def clone_schedule(doc, request):
    """Duplicate an existing schedule (keeps every column, heading, width, appearance)
    under a new name, replacing its filters.
    Body: {"source": "EQUIPMENT SCHEDULE" (name or id), "name": "EQUIPMENT SCHEDULE (E) - PHO HUNG",
           "filters": [{"heading": "STATUS", "equals": "EXISTING"}],   # optional; [] = no filters
           "keep_filters": false, "replace": true}"""
    from Autodesk.Revit.DB import (ViewSchedule, ViewDuplicateOption, ScheduleFilter,
                                   ScheduleFilterType)
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    src_key = data.get('source')
    name = data.get('name')
    if not src_key or not name:
        return _err('Required: source, name.')
    src = None
    for v in FilteredElementCollector(doc).OfClass(ViewSchedule):
        if v.IsTemplate:
            continue
        if v.Name == src_key or str(v.Id.Value) == str(src_key):
            src = v
            break
    if src is None:
        return _err('Source schedule "{}" not found.'.format(src_key), 404)
    t = Transaction(doc, 'OneTake: clone schedule -> {}'.format(name))
    _prep(t)
    t.Start()
    try:
        old_ids = []
        renamed_old = []
        if data.get("replace", True):
            old_ids = [v.Id for v in FilteredElementCollector(doc).OfClass(ViewSchedule)
                       if v.Name == name and not v.IsTemplate and v.Id != src.Id]
            for oid in old_ids:
                try:
                    doc.Delete(oid)
                except Exception:
                    # active view etc. cannot be deleted: rename it out of the way
                    ov = doc.GetElement(oid)
                    ov.Name = name + " - OLD"
                    renamed_old.append(oid.Value)
        new_id = src.Duplicate(ViewDuplicateOption.Duplicate)
        new = doc.GetElement(new_id)
        new.Name = name
        sdef = new.Definition
        if not data.get('keep_filters', False):
            while sdef.GetFilterCount() > 0:
                sdef.RemoveFilter(0)
        # optional extra fields, e.g. a hidden "Comments" column to filter on
        for af in (data.get("add_fields") or []):
            for sf in sdef.GetSchedulableFields():
                try:
                    nm = sf.GetName(doc)
                except Exception:
                    nm = None
                if nm == af.get("param"):
                    fld = sdef.AddField(sf)
                    fld.IsHidden = bool(af.get("hidden", True))
                    if af.get("heading"):
                        fld.ColumnHeading = af["heading"]
                    break
        missing = []
        for flt in (data.get('filters') or []):
            fid = None
            for i in range(sdef.GetFieldCount()):
                f = sdef.GetField(i)
                nm = None
                try:
                    nm = f.GetName()
                except Exception:
                    pass
                if f.ColumnHeading == flt.get('heading') or nm == flt.get('heading') \
                        or nm == flt.get('param'):
                    fid = f.FieldId
                    break
            if fid is None:
                missing.append(flt)
                continue
            ftype = ScheduleFilterType.Equal
            if flt.get('contains') is not None:
                ftype = ScheduleFilterType.Contains
                val = flt['contains']
            elif flt.get('not_equals') is not None:
                ftype = ScheduleFilterType.NotEqual
                val = flt['not_equals']
            else:
                val = flt.get('equals')
            sdef.AddFilter(ScheduleFilter(fid, ftype, str(val)))
        doc.Regenerate()
        info = _schedule_info(doc, new, 40)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'source_id': src.Id.Value, 'deleted_old_ids': [i.Value for i in old_ids], "renamed_old_ids": renamed_old,
            'missing_filters': missing, 'schedule': info}


@api.route('/element-info', methods=['POST'])
def element_info(doc, request):
    """Body: {"ids": [...], "params": ["Mark","Type Mark","Comments","Description"]}"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    ids = data.get('ids') or []
    params = data.get('params') or ['Mark', 'Type Mark', 'Comments', 'Description',
                                    'Manufacturer', 'Model']
    out = []
    for i in ids:
        el = doc.GetElement(ElementId(long(i)))
        if el is None:
            out.append({'id': i, 'error': 'not found'})
            continue
        d = {'id': i, 'category': el.Category.Name if el.Category else None,
             'class': el.GetType().Name}
        try:
            d['family'] = el.Symbol.FamilyName
            d['type'] = el.Symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        except Exception:
            pass
        try:
            d['level_id'] = el.LevelId.Value
        except Exception:
            pass
        try:
            bb = el.get_BoundingBox(None)
            if bb:
                d['bbox'] = [bb.Min.X, bb.Min.Y, bb.Max.X, bb.Max.Y]
            loc = el.Location
            if isinstance(loc, LocationPoint):
                d['xy'] = [loc.Point.X, loc.Point.Y]
        except Exception:
            pass
        for p in params:
            d[p] = _pval(el, p)
        out.append(d)
    return {'ok': True, 'elements': out}


def _find_view(doc, vname):
    if not vname:
        return doc.ActiveView
    for v in FilteredElementCollector(doc).OfClass(View):
        if not v.IsTemplate and v.Name == vname:
            return v
    return None


@api.route('/tags', methods=['POST'])
def list_or_create_tags(doc, request):
    """Body {"view": "Proposed Floor Plan"}  -> list independent tags in that view.
    Body {"view": ..., "items":[{"id": 4977940, "dx": 0, "dy": 1.5}], "tag_symbol_id": optional,
          "leader": false, "orientation": "Horizontal", "retag": false}  -> create tags.
    Offsets in FEET from the element location point."""
    if doc is None:
        return _err('No active document.', 409)
    from Autodesk.Revit.DB import IndependentTag, TagOrientation, Reference, TagMode
    data = request.data or {}
    view = _find_view(doc, data.get('view'))
    if view is None:
        return _err('View "{}" not found.'.format(data.get('view')), 404)
    existing = []
    already = {}
    for tg in FilteredElementCollector(doc, view.Id).OfClass(IndependentTag):
        hosts = []
        try:
            hosts = [r.ElementId.Value for r in tg.GetTaggedReferences()]
        except Exception:
            pass
        for h in hosts:
            already[h] = tg.Id.Value
        try:
            txt = tg.TagText
        except Exception:
            txt = None
        try:
            existing.append({'id': tg.Id.Value, 'hosts': hosts, 'text': txt,
                             'category': tg.Category.Name if tg.Category else None,
                             'x': tg.TagHeadPosition.X, 'y': tg.TagHeadPosition.Y})
        except Exception:
            existing.append({'id': tg.Id.Value, 'hosts': hosts, 'text': txt})
    items = data.get('items') or []
    if not items:
        return {'ok': True, 'view': view.Name, 'count': len(existing), 'tags': existing}
    orient = TagOrientation.Horizontal
    if str(data.get('orientation', '')).lower().startswith('v'):
        orient = TagOrientation.Vertical
    tag_type = None
    if data.get('tag_symbol_id'):
        tag_type = ElementId(long(data['tag_symbol_id']))
    leader = bool(data.get('leader', False))
    made, skipped, errors = [], [], []
    t = Transaction(doc, 'OneTake: tag {} elements'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for it in items:
            eid = long(it['id'])
            if eid in already and not data.get('retag'):
                skipped.append({'id': eid, 'tag_id': already[eid]})
                continue
            try:
                el = doc.GetElement(ElementId(eid))
                if el is None:
                    errors.append({'id': eid, 'error': 'not found'})
                    continue
                loc = el.Location
                if isinstance(loc, LocationPoint):
                    base = loc.Point
                else:
                    bb = el.get_BoundingBox(view)
                    base = (bb.Min + bb.Max) / 2.0
                pt = XYZ(base.X + float(it.get('dx', 0)), base.Y + float(it.get('dy', 0)), base.Z)
                ref = Reference(el)
                if tag_type is not None:
                    tag = IndependentTag.Create(doc, tag_type, view.Id, ref, leader, orient, pt)
                else:
                    tag = IndependentTag.Create(doc, view.Id, ref, leader,
                                                TagMode.TM_ADDBY_CATEGORY, orient, pt)
                doc.Regenerate()
                try:
                    txt = tag.TagText
                except Exception:
                    txt = None
                made.append({'id': eid, 'tag_id': tag.Id.Value, 'text': txt})
            except Exception as ex:
                errors.append({'id': eid, 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'view': view.Name, 'tags': made, 'skipped': skipped,
            'errors': errors, 'count': len(made)}


@api.route('/tag-family-from', methods=['POST'])
def tag_family_from(doc, request):
    """Derive a new tag family from a loaded one (e.g. make a Multi-Category tag out of
    'Plumbing Fixture Tag' so one Type-Mark tag works on every equipment category).
    Body: {"source_family": "Plumbing Fixture Tag", "new_name": "OneTake Equipment Tag",
           "category": "OST_MultiCategoryTags"}"""
    from Autodesk.Revit.DB import (Family, Category, SaveAsOptions, IFamilyLoadOptions)
    import os, tempfile
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    src_name = data.get('source_family')
    new_name = data.get('new_name') or 'OneTake Equipment Tag'
    cat_name = data.get('category') or 'OST_MultiCategoryTags'
    src = None
    for f in FilteredElementCollector(doc).OfClass(Family):
        if f.Name == src_name:
            src = f
            break
    if src is None:
        return _err('Family "{}" not found.'.format(src_name), 404)
    # already there?
    for f in FilteredElementCollector(doc).OfClass(Family):
        if f.Name == new_name:
            syms = [doc.GetElement(i) for i in f.GetFamilySymbolIds()]
            return {'ok': True, 'existing': True, 'family_id': f.Id.Value,
                    'symbol_ids': [s.Id.Value for s in syms],
                    'category': f.FamilyCategory.Name if f.FamilyCategory else None}
    fam_doc = None
    # reuse an already-open family doc for this family (a previous failed call)
    for d in HOST_APP.uiapp.Application.Documents:
        try:
            if d.IsFamilyDocument and d.Title.split(".")[0] == src_name:
                fam_doc = d
        except Exception:
            pass
    if fam_doc is None:
        fam_doc = doc.EditFamily(src)
    try:
        t = Transaction(fam_doc, "OneTake: recategorize tag")
        t.Start()
        try:
            cat = fam_doc.Settings.Categories.get_Item(getattr(BuiltInCategory, cat_name))
            fam_doc.OwnerFamily.FamilyCategory = cat
            t.Commit()
        except Exception as ex:
            t.RollBack()
            raise Exception("recategorize to {} failed: {}".format(cat_name, ex))
        labels = []
        try:
            from Autodesk.Revit.DB import TextElement
            for te in FilteredElementCollector(fam_doc).OfClass(TextElement):
                labels.append({'id': te.Id.Value, 'class': te.GetType().Name,
                               'text': getattr(te, 'Text', None)})
        except Exception:
            pass
        path = os.path.join(tempfile.gettempdir(), new_name + '.rfa')
        if os.path.exists(path):
            os.remove(path)
        opts = SaveAsOptions()
        opts.OverwriteExistingFile = True
        fam_doc.SaveAs(path, opts)
        newfam = fam_doc.LoadFamily(doc)
    finally:
        try:
            fam_doc.Close(False)
        except Exception:
            pass
    if newfam is None:
        return _err('LoadFamily returned None', 500)
    t2 = Transaction(doc, 'OneTake: activate tag symbols')
    _prep(t2)
    t2.Start()
    syms = []
    for i in newfam.GetFamilySymbolIds():
        s = doc.GetElement(i)
        if not s.IsActive:
            s.Activate()
        syms.append(s.Id.Value)
    t2.Commit()
    return {'ok': True, 'existing': False, 'family_id': newfam.Id.Value, 'name': newfam.Name,
            'category': newfam.FamilyCategory.Name if newfam.FamilyCategory else None,
            'symbol_ids': syms, 'saved_as': path, 'labels': labels}


@api.route('/docs', methods=['GET'])
def list_docs(doc):
    """Open documents (project + family docs), for recovery after failed EditFamily."""
    import System
    System.GC.Collect()
    System.GC.WaitForPendingFinalizers()
    out = []
    for d in HOST_APP.uiapp.Application.Documents:
        try:
            out.append({'title': d.Title, 'family': d.IsFamilyDocument,
                        'modifiable': d.IsModifiable, 'path': d.PathName})
        except Exception as ex:
            out.append({'error': str(ex)})
    return {'ok': True, 'docs': out}


@api.route('/close-doc', methods=['POST'])
def close_doc(doc, request):
    """Body {"title": "Plumbing Fixture Tag.rfa"} -> close that (family) doc without saving."""
    import System
    System.GC.Collect()
    System.GC.WaitForPendingFinalizers()
    title = (request.data or {}).get('title')
    for d in list(HOST_APP.uiapp.Application.Documents):
        try:
            if d.Title == title or d.Title.split('.')[0] == title:
                if not d.IsFamilyDocument:
                    return _err('Refusing to close a project document.', 400)
                ok = d.Close(False)
                return {'ok': True, 'closed': bool(ok), 'title': title}
        except Exception as ex:
            return _err('close failed: {}'.format(ex), 500)
    return _err('doc "{}" not open'.format(title), 404)


# -- Move / rotate elements, re-point walls -------------------------------------

def _elem_center(el, view=None):
    loc = el.Location
    if isinstance(loc, LocationPoint):
        return loc.Point
    bb = el.get_BoundingBox(view)
    if bb is None:
        return None
    return (bb.Min + bb.Max) * 0.5


@api.route('/move', methods=['POST'])
def move_elements(doc, request):
    """Move / rotate elements. FEET, degrees.
    Body: {"items": [{"id": 1, "dx": 1.5, "dy": -2},          # relative
                     {"id": 2, "to": [30.5, 17.5]},           # absolute: location point (or bbox center) -> to
                     {"id": 3, "to": [..], "by": "bbox"},     # use bbox center as the reference point
                     {"id": 4, "rotate_deg": 90}]}            # rotate about its own point / bbox center
    Hosted elements move along their host; walls can be moved too (use /wall-move to re-point)."""
    if doc is None:
        return _err('No active document.', 409)
    items = (request.data or {}).get('items') or []
    if not items:
        return _err('Required: items.')
    out = []
    t = Transaction(doc, 'OneTake: move {} elements'.format(len(items)))
    _prep(t)
    t.Start()
    try:
        for it in items:
            eid = long(it['id'])
            el = doc.GetElement(ElementId(eid))
            if el is None:
                out.append({'id': eid, 'error': 'not found'})
                continue
            res = {'id': eid}
            try:
                if it.get("flip"):
                    try:
                        el.flipFacing()
                        res["flipped"] = True
                    except Exception as ex:
                        res["flip_error"] = str(ex)
                if it.get("flip_hand"):
                    try:
                        el.flipHand()
                    except Exception as ex:
                        res["flip_hand_error"] = str(ex)
                if it.get('rotate_deg'):
                    c = _elem_center(el)
                    axis = Line.CreateBound(c, c + XYZ.BasisZ)
                    ElementTransformUtils.RotateElement(doc, el.Id, axis,
                                                        math.radians(float(it['rotate_deg'])))
                    doc.Regenerate()
                    res['rotated'] = float(it['rotate_deg'])
                dx = dy = 0.0
                if it.get('to') is not None:
                    ref = None
                    if it.get('by') == 'bbox':
                        bb = el.get_BoundingBox(None)
                        if bb is not None:
                            ref = (bb.Min + bb.Max) * 0.5
                    if ref is None:
                        ref = _elem_center(el)
                    if ref is None:
                        res['error'] = 'no location'
                        out.append(res)
                        continue
                    dx = float(it['to'][0]) - ref.X
                    dy = float(it['to'][1]) - ref.Y
                else:
                    dx = float(it.get('dx', 0))
                    dy = float(it.get('dy', 0))
                if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                    ElementTransformUtils.MoveElement(doc, el.Id, XYZ(dx, dy, 0))
                    doc.Regenerate()
                res['moved'] = [round(dx, 3), round(dy, 3)]
                c = _elem_center(el)
                if c is not None:
                    res['now'] = [round(c.X, 2), round(c.Y, 2)]
                bb = el.get_BoundingBox(None)
                if bb is not None:
                    res['bbox'] = [round(bb.Min.X, 2), round(bb.Min.Y, 2), round(bb.Max.X, 2), round(bb.Max.Y, 2)]
            except Exception as ex:
                res['error'] = str(ex)
            out.append(res)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'results': out}


@api.route('/wall-move', methods=['POST'])
def wall_move(doc, request):
    """Re-point walls (keeps hosted doors etc. where possible). FEET.
    Body: {"walls": [{"id": 123, "start": [x, y], "end": [x, y]}]}"""
    if doc is None:
        return _err('No active document.', 409)
    walls = (request.data or {}).get('walls') or []
    if not walls:
        return _err('Required: walls.')
    out = []
    t = Transaction(doc, 'OneTake: re-point {} walls'.format(len(walls)))
    _prep(t)
    t.Start()
    try:
        for w in walls:
            wid = long(w['id'])
            wall = doc.GetElement(ElementId(wid))
            if wall is None or not isinstance(wall, Wall):
                out.append({'id': wid, 'error': 'not a wall'})
                continue
            try:
                lc = wall.Location
                z = lc.Curve.GetEndPoint(0).Z
                p0 = XYZ(float(w['start'][0]), float(w['start'][1]), z)
                p1 = XYZ(float(w['end'][0]), float(w['end'][1]), z)
                lc.Curve = Line.CreateBound(p0, p1)
                doc.Regenerate()
                c = wall.Location.Curve
                out.append({'id': wid, 'start': [round(c.GetEndPoint(0).X, 3), round(c.GetEndPoint(0).Y, 3)],
                            'end': [round(c.GetEndPoint(1).X, 3), round(c.GetEndPoint(1).Y, 3)],
                            'length_ft': round(c.Length, 3)})
            except Exception as ex:
                out.append({'id': wid, 'error': str(ex)})
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'results': out}


@api.route('/curtain-grid', methods=['POST'])
def curtain_grid(doc, request):
    """Inspect / edit a curtain wall grid. FEET.
    Body: {"wall_id": 123}                                  -> list panels (id, type, bbox) + grid lines
          {"wall_id": 123, "add_at": [[x,y], ...], "u": false} -> add grid lines through those points
          {"wall_id": 123, "remove_ids": [...]}             -> remove grid lines"""
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    wall = doc.GetElement(ElementId(long(data.get('wall_id') or 0)))
    grid = getattr(wall, 'CurtainGrid', None)
    if grid is None:
        return _err('Not a curtain wall.', 400)
    added, removed, errors = [], [], []
    if data.get('add_at') or data.get('remove_ids'):
        t = Transaction(doc, 'OneTake: curtain grid')
        _prep(t)
        t.Start()
        try:
            for pt in (data.get('add_at') or []):
                try:
                    z = wall.Location.Curve.GetEndPoint(0).Z + 3.0
                    gl = grid.AddGridLine(bool(data.get('u', False)), XYZ(float(pt[0]), float(pt[1]), z), False)
                    added.append(gl.Id.Value)
                except Exception as ex:
                    errors.append({'add_at': pt, 'error': str(ex)})
            for gid in (data.get('remove_ids') or []):
                try:
                    gl = doc.GetElement(ElementId(long(gid)))
                    try:
                        gl.Lock = False
                    except Exception:
                        pass
                    segs = list(gl.AllSegmentCurves)
                    for sc in segs:
                        gl.RemoveSegment(sc)
                    removed.append(gid)
                except Exception as ex:
                    errors.append({'remove': gid, 'error': str(ex)})
            doc.Regenerate()
            t.Commit()
        except Exception as ex:
            t.RollBack()
            return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    panels = []
    for pid in grid.GetPanelIds():
        p = doc.GetElement(pid)
        bb = p.get_BoundingBox(None)
        try:
            tname = p.Symbol.FamilyName + ' : ' + p.Symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        except Exception:
            tname = p.GetType().Name
        panels.append({'id': pid.Value, 'type': tname,
                       'bbox': [round(bb.Min.X, 2), round(bb.Min.Y, 2), round(bb.Max.X, 2), round(bb.Max.Y, 2)] if bb else None})
    lines = []
    for lid in list(grid.GetUGridLineIds()) + list(grid.GetVGridLineIds()):
        gl = doc.GetElement(lid)
        try:
            c = gl.FullCurve
            lines.append({'id': lid.Value, 'u': lid in grid.GetUGridLineIds(),
                          'p0': [round(c.GetEndPoint(0).X, 2), round(c.GetEndPoint(0).Y, 2), round(c.GetEndPoint(0).Z, 2)],
                          'p1': [round(c.GetEndPoint(1).X, 2), round(c.GetEndPoint(1).Y, 2), round(c.GetEndPoint(1).Z, 2)]})
        except Exception:
            lines.append({'id': lid.Value})
    return {'ok': True, 'added': added, 'removed': removed, 'errors': errors,
            'panels': sorted(panels, key=lambda d: (d['bbox'] or [0])[0]), 'grid_lines': lines}


@api.route('/views', methods=['GET'])
def list_views(doc):
    """Floor plans, ceiling plans, schedules-free view list: id, name, type, is_active."""
    if doc is None:
        return _err('No active document.', 409)
    out = []
    active = doc.ActiveView.Id
    for v in FilteredElementCollector(doc).OfClass(View):
        if v.IsTemplate:
            continue
        vt = str(v.ViewType)
        if vt not in ('FloorPlan', 'CeilingPlan', 'DrawingSheet', 'ThreeD', 'Elevation', 'Section', 'AreaPlan'):
            continue
        d = {'id': v.Id.Value, 'name': v.Name, 'type': vt, 'active': v.Id == active}
        try:
            d['sheet_number'] = v.SheetNumber
        except Exception:
            pass
        out.append(d)
    out.sort(key=lambda d: (d['type'], d['name']))
    return {'ok': True, 'count': len(out), 'views': out}


@api.route('/open-view', methods=['POST'])
def open_view(uiapp, request):
    """Body {"name": "Proposed Floor Plan"} -> make that view active in Revit."""
    uidoc = uiapp.ActiveUIDocument
    if uidoc is None:
        return _err('No active document.', 409)
    doc = uidoc.Document
    name = (request.data or {}).get('name')
    for v in FilteredElementCollector(doc).OfClass(View):
        if not v.IsTemplate and v.Name == name:
            uidoc.RequestViewChange(v)
            return {'ok': True, 'view_id': v.Id.Value, 'name': v.Name, 'type': str(v.ViewType)}
    return _err('View "{}" not found.'.format(name), 404)


@api.route('/save', methods=['POST'])
def save_doc(doc):
    """Save the active document in place (doc.Save())."""
    if doc is None:
        return _err('No active document.', 409)
    try:
        doc.Save()
    except Exception as ex:
        return _err('Save failed: {}'.format(ex), 500)
    return {'ok': True, 'path': doc.PathName, 'title': doc.Title}


@api.route('/export-view', methods=['POST'])
def export_view(doc, request):
    """Export a view to PNG. Body {"name": "Proposed Floor Plan", "path": "C:/tmp/view.png",
    "width_px": 3000, "crop": [xmin, ymin, xmax, ymax] (feet, optional; sets the crop box)}"""
    from Autodesk.Revit.DB import (ImageExportOptions, ImageFileType, ExportRange,
                                   ZoomFitType, ImageResolution, BoundingBoxXYZ)
    from System.Collections.Generic import List
    import os
    if doc is None:
        return _err('No active document.', 409)
    data = request.data or {}
    view = _find_view(doc, data.get('name'))
    if view is None:
        return _err('View not found.', 404)
    path = data.get('path') or os.path.join(os.environ.get('TEMP', 'C:\'), 'onetake_view.png')
    crop = data.get('crop')
    if crop:
        t = Transaction(doc, 'OneTake: crop view')
        _prep(t)
        t.Start()
        try:
            bb = BoundingBoxXYZ()
            bb.Min = XYZ(float(crop[0]), float(crop[1]), -10)
            bb.Max = XYZ(float(crop[2]), float(crop[3]), 100)
            view.CropBox = bb
            view.CropBoxActive = True
            view.CropBoxVisible = False
            t.Commit()
        except Exception as ex:
            t.RollBack()
            return _err('crop failed: {}'.format(ex), 500)
    opts = ImageExportOptions()
    opts.ExportRange = ExportRange.SetOfViews
    ids = List[ElementId]()
    ids.Add(view.Id)
    opts.SetViewsAndSheets(ids)
    opts.FilePath = path
    opts.HLRandWFViewsFileType = ImageFileType.PNG
    opts.ShadowViewsFileType = ImageFileType.PNG
    opts.ZoomType = ZoomFitType.FitToPage
    opts.PixelSize = int(data.get('width_px') or 3000)
    opts.ImageResolution = ImageResolution.DPI_150
    try:
        doc.ExportImage(opts)
    except Exception as ex:
        return _err('ExportImage failed: {}'.format(ex), 500)
    # Revit appends " - Floor Plan - <name>" to the file name; find what it wrote
    d = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    written = [os.path.join(d, f) for f in os.listdir(d) if f.startswith(stem) and f.lower().endswith('.png')]
    return {'ok': True, 'files': written}


# ── Dev runner: execute a script from dev_scripts/ without reloading ─────────

@api.route('/dev/run', methods=['POST'])
def dev_run(uiapp, request):
    """Body {"file": "scratch.py", "args": {...}} -> execfile(dev_scripts/<file>) with globals
    doc, uiapp, uidoc, args, result. Returns {"ok": true, "result": <result>} or the FULL
    traceback on failure. Files are restricted to dev_scripts/ (no path escapes)."""
    import os, traceback
    data = request.data or {}
    fname = data.get('file') or 'scratch.py'
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev_scripts')
    path = os.path.abspath(os.path.join(base, fname))
    if not path.startswith(base + os.sep) or not path.lower().endswith('.py'):
        return _err('file must be a .py inside dev_scripts/', 400)
    if not os.path.exists(path):
        return _err('not found: {}'.format(path), 404)
    uidoc = uiapp.ActiveUIDocument
    doc = uidoc.Document if uidoc else None
    g = {'__name__': '__onetake_dev__', '__file__': path,
         'doc': doc, 'uiapp': uiapp, 'uidoc': uidoc,
         'args': data.get('args') or {}, 'result': None,
         'HOST_APP': HOST_APP, 'Transaction': Transaction, '_prep': _prep, '_err': _err,
         'FilteredElementCollector': FilteredElementCollector, 'ElementId': ElementId, 'XYZ': XYZ}
    try:
        execfile(path, g)
    except Exception:
        return {'ok': False, 'file': fname, 'traceback': traceback.format_exc()}
    out = g.get('result')
    try:
        import json
        json.dumps(out)
    except Exception:
        out = repr(out)
    return {'ok': True, 'file': fname, 'result': out}

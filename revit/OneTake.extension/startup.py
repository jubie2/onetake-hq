# -*- coding: utf-8 -*-
"""OneTake routes API — typed verb layer for driving Revit from Claude.

IronPython 2.7 ONLY. No f-strings, print is a statement.
Registered at pyRevit startup; edit -> RELOAD pyRevit -> curl to test.

Smoke test:
    curl http://localhost:48884/onetake-v1/status
"""
from pyrevit import routes, HOST_APP, __version__ as PYREVIT_VERSION

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
)

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


# ── Read-only verbs ──────────────────────────────────────────────

@api.route('/status', methods=['GET'])
def status():
    """Is the server alive, what are we attached to."""
    return {
        'ok': True,
        'revit_version': HOST_APP.version,
        'revit_build': HOST_APP.build,
        'pyrevit_version': str(PYREVIT_VERSION),
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
    t.Start()
    try:
        for start, end in pairs:
            if start.DistanceTo(end) < 0.01:  # degenerate segment, feet
                continue
            line = Line.CreateBound(start, end)
            wall = Wall.Create(doc, line, level.Id, False)
            if wall_type_id:
                wall.WallType = doc.GetElement(wall_type_id)
            hp = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
            if hp:
                hp.Set(float(height))
            created.append(wall.Id.Value)
        t.Commit()
    except Exception as ex:
        t.RollBack()
        return _err('Revit API error (nothing committed): {}'.format(ex), 500)
    return {'ok': True, 'wall_ids': created, 'count': len(created)}

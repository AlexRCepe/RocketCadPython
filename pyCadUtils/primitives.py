import cadquery as cq
from math import pi

EPS = 1e-9

def _normalize_base_to_z0(result: cq.Workplane) -> cq.Workplane:
    try:
        bbox = result.val().BoundingBox()
        return result.translate((0, 0, -bbox.zmin))
    except Exception:
        return result

def create_cylinder(wp: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
    outer = wp.circle(radius).extrude(height)

    if thickness is None or thickness <= 0:
        result = outer
    else:
        inner_r = max(radius - thickness, 0.0)
        if inner_r <= EPS:
            result = outer
        else:
            inner = wp.circle(inner_r).extrude(height)
            result = outer.cut(inner)

    # return _normalize_base_to_z0(result)
    return result

def create_cone(wp: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
    # Outer cone (profile drawn on a rotated workplane so revolve gives cone with base on upmost face)
    outer = (
        wp.workplane(offset=0)
        .transformed(rotate=(90, 0, 0))
        .polyline([(0, 0), (radius, 0), (0, height)])
        .close()
        .revolve(360)
    )

    if thickness is None or thickness <= 0:
        result = outer
    else:
        # inner base radius = radius - thickness
        # inner apex is shifted axially by a proportional amount: height_difference = thickness * (height / radius)
        if radius <= EPS or height <= EPS:
            inner_r = max(radius - thickness, 0.0)
            inner = (
                wp.workplane(offset=0)
                .transformed(rotate=(90, 0, 0))
                .polyline([(0, 0), (inner_r, 0), (0, height)])
                .close()
                .revolve(360)
            )
        else:
            inner_r = max(radius - thickness, 0.0)
            height_difference = thickness * (height / radius)
            inner_apex_z = max(height - height_difference, EPS)
            inner = (
                wp.workplane(offset=0)
                .transformed(rotate=(90, 0, 0))
                .polyline([(0, 0), (inner_r, 0), (0, inner_apex_z)])
                .close()
                .revolve(360)
            )

        result = outer.cut(inner)

    # return _normalize_base_to_z0(result)
    return result

def create_transition(wp: cq.Workplane, height: float, radius1: float, radius2: float, thickness: float) -> cq.Workplane:
    # Outer frustum (base at z=0 radius2, top at z=height radius1)
    outer = wp.circle(radius2).workplane(offset=height).circle(radius1).loft(combine=True)

    if thickness is None or thickness <= 0:
        result = outer
    else:
        # simple radial shrink for inner loft (as in parts.py)
        inner_base_r = max(radius2 - thickness, 0.0)
        inner_top_r = max(radius1 - thickness, 0.0)
        inner = wp.circle(inner_base_r).workplane(offset=height).circle(inner_top_r).loft(combine=True)
        result = outer.cut(inner)

    # return _normalize_base_to_z0(result)
    return result

def create_trapezoidal_fin(wp: cq.Workplane, root_chord: float, tip_chord: float, span: float, sweep: float, thickness: float) -> cq.Workplane:
    # wp = cq.Workplane("XZ")
    # Define the 2D profile of the fin
    points = [
        (0, 0),  # Root leading edge
        (0, root_chord),  # Root trailing edge
        (span, root_chord - sweep),  # Tip trailing edge
        (span, root_chord - sweep - tip_chord),  # Tip leading edge
    ]

    # Create the fin profile and extrude it to create a 3D fin
    fin = (
        wp.polyline(points)
        .close()
        .extrude(thickness)
    )

    fin = fin.rotate((0,0,0), (1,0,0), 90)

    return fin
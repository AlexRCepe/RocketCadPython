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

def create_cone(wp: cq.Workplane, shape: str, height: float, radius: float, thickness: float, k: float = 0.7) -> cq.Workplane:
    """
    Create a nosecone with various shape profiles.
    
    Parameters:
    wp (cq.Workplane): The workplane to create the cone on.
    shape (str): The shape type of the nosecone. Options: 'CONICAL', 'OGIVE', 'ELLIPTICAL', 'POWER_LAW'
    height (float): The length/height of the nosecone.
    radius (float): The radius of the nosecone at the base.
    thickness (float): The thickness of the cone wall.
    k (float): The exponent for POWER_LAW shape (default: 0.7).
    
    Returns:
    cq.Workplane: A nosecone solid with the specified shape.
    """
    
    # Define shape functions
    shapes = {
        'CONICAL': lambda x, R, L: x * R / L,
        'OGIVE': lambda x, R, L: (((R**2 + L**2)/2.0/R)**2 - (L - x)**2)**(0.5) + R - ((R**2 + L**2)/2.0/R),
        'ELLIPTICAL': lambda x, R, L: R * (2*(x/L) - (x/L)**2)**(0.5),
        'POWER_LAW': lambda x, R, L: R * (x/L)**k,
    }
    
    # Validate and select shape function
    if shape not in shapes:
        raise ValueError(f"Invalid shape '{shape}'. Must be one of: {list(shapes.keys())}")
    
    conical_shape = shapes[shape]

    # Parameters
    R = radius
    L = height
    num_steps = 100

    # --- Generate Outer Solid ---
    outer_points = []
    for i in range(num_steps + 1):
        h = i * L / num_steps
        r = conical_shape(h, R, L)
        outer_points.append((r, h))
    
    outer_cone = (
            wp.workplane(offset=0)
            .spline(outer_points)  # Draw the side (Curve or Line)
            .lineTo(0, L)            # Draw the top cap (Flat Line)
            .close()                 # Draw the axis (Straight Line back to start)
            .revolve()
        )

    # --- Generate Inner Solid (The Void) ---
    # Inner cone has reduced radius (R - thickness) and proportionally reduced height
    inner_points = []
    inner_r = max(R - thickness, 1e-9)
    inner_l = max(L - thickness * (L / R), 1e-9)
    y_offset = thickness * (L / R) 
    
    for i in range(num_steps + 1):
        y = i * inner_l / num_steps
        x = conical_shape(y, inner_r, inner_l)
        inner_points.append((x, y + y_offset))

    inner_cone = (
            wp.workplane(offset=0)
            .spline(inner_points)  # Draw the side (Curve or Line)
            .lineTo(0, inner_l + y_offset)            # Draw the top cap (Flat Line)
            .close()                 # Draw the axis (Straight Line back to start)
            .revolve()
        )

    # --- Boolean Operation ---
    # Subtract the inner void from the outer shape
    result = outer_cone.cut(inner_cone)
    
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
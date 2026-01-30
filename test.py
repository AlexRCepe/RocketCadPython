import cadquery as cq
from cadquery.vis import show
from math import sin, cos, pi


def make_hollow_cone(radius, length, thickness):
    """
    Create a hollow cone using CadQuery.

    Parameters:
    radius (float): The radius of the cone at the base.
    length (float): The length of the cone.
    thickness (float): The thickness of the cone wall.

    Returns:
    A CadQuery solid object representing the hollow cone.
    """
    cone = (cq.Workplane("XY")
            .transformed(rotate=(90,0, 0))
            .polyline([(0,0), (radius,0), (0,length)])
            .close()
            .revolve(360)
        )
    
    inner_cone = (cq.Workplane("XY")
            .transformed(rotate=(90,0, 0))
            .polyline([(0,0), (radius - thickness,0), (0,length - thickness)])
            .close()
            .revolve(360)
        )

    hollow_cone = cone.cut(inner_cone)

    hollow_cone_bbox = hollow_cone.val().BoundingBox()
    hollow_cone = hollow_cone.translate((0, 0, -hollow_cone_bbox.zmin))

    return hollow_cone

def make_hollow_cylinder(radius, length, thickness):
    """
    Create a hollow cylinder using CadQuery.

    Parameters:
    radius (float): The radius of the cylinder.
    length (float): The length of the cylinder.
    thickness (float): The thickness of the cylinder wall.

    Returns:
    A CadQuery solid object representing the hollow cylinder.
    """
    hollow_cylinder = (
    cq.Workplane("front")
    .cylinder(length,radius)
    .faces("+Z or -Z")
    .shell(-thickness)
    )

    # Place the cylinder base at Z=0 (for easier positioning later)
    hollow_cylinder_bbox = hollow_cylinder.val().BoundingBox()
    hollow_cylinder = hollow_cylinder.translate((0, 0, -hollow_cylinder_bbox.zmin))

    return hollow_cylinder

def make_cone_on_cylinder(cone_radius, cone_length, cone_thickness, cylinder_radius, cylinder_length, cylinder_thickness):
    """
    Create a composite object with a hollow cone on top of a hollow cylinder.

    Parameters:
    cone_radius (float): The radius of the cone at the base.
    cone_length (float): The length of the cone.
    cone_thickness (float): The thickness of the cone wall.
    cylinder_radius (float): The radius of the cylinder.
    cylinder_length (float): The length of the cylinder.
    cylinder_thickness (float): The thickness of the cylinder wall.

    Returns:
    A CadQuery solid object representing the cone on cylinder.
    """
    # Create the hollow cone
    cone = make_hollow_cone(cone_radius, cone_length, cone_thickness)

    # Create the hollow cylinder
    cylinder = make_hollow_cylinder(cylinder_radius, cylinder_length, cylinder_thickness)

    # Position the cone on top of the cylinder
    cone_on_cylinder = cone.translate((0, 0, cylinder_length))

    assembly = cylinder.union(cone_on_cylinder)

    return assembly

# def hollow_transition(radius_bodytube, radius_cone, length,thickness):
#     transition = (cq.Workplane("front")
#                     .circle(radius_bodytube)
#                     .workplane(offset=length)
#                     .circle(radius_cone)
#                     .loft(combine=True)
#                     .faces("+Z or -Z")
#                     .shell(-thickness)
#                   )
#     return transition
def hollow_transition(radius_bodytube, radius_cone, length, thickness):
    """
    Create a hollow transition (frustum) using loft.
    """
    # Outer loft
    outer = (
        cq.Workplane("XY")
        .circle(radius_bodytube)
        .workplane(offset=length)
        .circle(radius_cone)
        .loft()
    )

    # Inner loft
    inner = (
        cq.Workplane("XY")
        .circle(max(radius_bodytube - thickness, 0))
        .workplane(offset=length)
        .circle(max(radius_cone - thickness, 0))
        .loft()
    )

    # Hollow frustum
    hollow = outer.cut(inner)
        # Place the cylinder base at Z=0 (for easier positioning later)
    hollow_bbox = hollow.val().BoundingBox()
    hollow = hollow.translate((0, 0, -hollow_bbox.zmin))

    return hollow

def rocket(body_tube,cone,transition):
    transition = transition.translate((0,0,body_tube.val().BoundingBox().zmax))
    cone = cone.translate((0,0,transition.val().BoundingBox().zmax))
    rocket = body_tube.union(transition).union(cone)
    return rocket
    

def make_bearing_pillow_block(height, width, thickness, diameter, padding):
    
    result = (cq.Workplane("XY")
              .box(height, width, thickness)
              .faces(">Z")
              .workplane()
              .hole(diameter)
              .faces(">Z")
              .workplane()
              .rect(height - padding, width - padding, forConstruction=True)
              .vertices()
              .cboreHole(2.4, 4.4, 2.1)
              .edges("|Z")
              .fillet(2.0)
              )

    # Render the solid
    cq.exporters.export(result, "result.stl")
    show(result)

def prueba():


    result = (
        cq.Workplane("XZ")
        .polyline([(0,0), (5,0), (0,10)])  # half-profile of a cone
        .close()
        .revolve(360)
        .faces("-Z")
        .shell(-0.5)
    )
 
    
    show(result)

def create_trapezoidal_fin(wp: cq.Workplane, root_chord: float, tip_chord: float, span: float, sweep: float, thickness: float) -> cq.Workplane:
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
    base = wp.rect(span, root_chord).extrude(thickness)

    fin = fin.rotate((0,0,0), (1,0,0), 90).translate((0,5,3))
    project= base.add(fin)
    return project

def create_FinSet(wp: cq.Workplane, count: int, root_chord: float, tip_chord: float, span: float, sweep: float, position: float, thickness: float, body_diameter: float) -> cq.Workplane:
        """
        Create Fin Set geometry on the given workplane.
        Returns a Workplane object with the FinSet solid positioned with base at the given workplane.
        """
        body_radius = body_diameter / 2.0

        # wp = wp.offset2D(position).rotate((0,0,0),(0,1,0),90).offset2D(-body_radius)
        wp = wp.transformed((90,0,0))
        fin = create_trapezoidal_fin(wp, root_chord, tip_chord, span, sweep, thickness)

        finset = None
        for i in range(count):
            angle_deg = i * 360.0 / count

            # copy and position:
            # 1) translate so root sits radially at body_radius
            # 2) translate axially to `position`
            # 3) rotate around the rocket axis (Z) at origin
            # f = fin.translate((position, body_radius, 0.0))
            # rotate around origin Z (CadQuery rotate takes degrees)
            # f = fin.rotate((0, 0, 0), (0, 0, 1), angle_deg)

            if finset is None:
                finset = fin
            else:
                finset = finset.union(fin)

        # If no fins (count == 0) return an empty workplane
        if finset is None:
            return cq.Workplane("XY")  # empty
        # normalize base if needed (optional)
        try:
            bbox = finset.val().BoundingBox()
            finset = finset.translate((0, 0, -bbox.zmin))
        except Exception:
            pass

        return finset
EPS = 1e-9

def create_cone(wp: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
    # 1. Define the Shape Function
    conical_shape = lambda x, R, L, k: R * (x/L)**k
    
    # Parameters
    R = radius
    L = height
    k = 2.0
    num_steps = 20

    # --- Generate Outer Solid ---
    outer_points = []
    for i in range(num_steps + 1):
        h = i * L / num_steps
        r = conical_shape(h, R, L, k)
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
        x = conical_shape(y, inner_r, inner_l, k)
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



# Export to verify
# cq.exporters.export(result, "hollow_cone.step")


# Example usage
# cone_on_cylinder = make_cone_on_cylinder(
#    cone_radius=5, cone_length=10, cone_thickness=1,
#    cylinder_radius=7, cylinder_length=15, cylinder_thickness=1
# )

# make_bearing_pillow_block(height=60, width=80, thickness=10, diameter=22, padding=12)

# hollow_cone = make_hollow_cone(radius=20, length=50, thickness=5)
# cq.exporters.export(hollow_cone, "hollow_cone.stl")

print(cq.__version__)
# show(make_hollow_cylinder(10,50,2))
# show(create_trapezoidal_fin(cq.Workplane("XY"),20,10,10,10,1), alpha=0.8)
show(create_cone(cq.Workplane('XY'), height=20, radius=10, thickness=3.8), alpha=0.6)
# show(create_FinSet(cq.Workplane("XY"),4,20,10,10,10,30,1,20), alpha=0.8)
# show(make_cone_on_cylinder(5,20,1,5,50,1), alpha=0.3)
# show(hollow_transition(10,5,20,2),alpha=0.7)
# prueba()

# body_tube = make_hollow_cylinder(15,100,2)
# cone = make_hollow_cone(10,30,2)
# transition = hollow_transition(15,10,20,2)

# rocket_model = rocket(body_tube,cone,transition)
# show(rocket_model, alpha=0.5)

# cq.exporters.export(create_cone(cq.Workplane('XY'), height=20, radius=10, thickness=3.7), "ojiva.stl")
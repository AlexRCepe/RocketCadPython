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
show(make_hollow_cone(20,50,2), alpha=0.8)
# show(make_cone_on_cylinder(5,20,1,5,50,1), alpha=0.3)
# show(hollow_transition(10,5,20,2),alpha=0.7)
# prueba()

body_tube = make_hollow_cylinder(15,100,2)
cone = make_hollow_cone(10,30,2)
transition = hollow_transition(15,10,20,2)

rocket_model = rocket(body_tube,cone,transition)
# show(rocket_model, alpha=0.5)

#cq.exporters.export(cone_on_cylinder, "cone_on_cylinder.stl")
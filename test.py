import cadquery as cq

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
    # Create the outer cone
    outer_cone = (
        cq.Workplane("XY")
        .sphere(radius, angle1=0, angle2=90)
        .translate((0, 0, -length / 2))
    )

    # Create the inner cone
    inner_cone = (
        cq.Workplane("XY")
        .sphere(radius - thickness, angle1=0, angle2=90)
        .translate((0, 0, -length / 2))
    )

    # Subtract the inner cone from the outer cone to create the hollow cone
    hollow_cone = outer_cone.cut(inner_cone)

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
    # Create the outer cylinder
    outer_cylinder = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length)
    )

    # Create the inner cylinder
    inner_cylinder = (
        cq.Workplane("XY")
        .circle(radius - thickness)
        .extrude(length)
    )

    # Subtract the inner cylinder from the outer cylinder to create the hollow cylinder
    hollow_cylinder = outer_cylinder.cut(inner_cylinder)

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
    print(type(cylinder))
    # Position the cone on top of the cylinder
    cone_on_cylinder = cone.translate((0, 0, cylinder_length))
    assembly = cylinder.union(cone_on_cylinder)

    return assembly

# Example usage
cone_on_cylinder = make_cone_on_cylinder(
    cone_radius=5, cone_length=10, cone_thickness=1,
    cylinder_radius=7, cylinder_length=15, cylinder_thickness=1
)

cq.exporters.export(cone_on_cylinder, "cone_on_cylinder.stl")
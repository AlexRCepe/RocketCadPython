import cadquery as cq
from abc import ABC, abstractmethod
from .primitives import create_cylinder, create_cone, create_transition, create_trapezoidal_fin

class Part3DBuilder(ABC):
    @classmethod
    @abstractmethod
    def addPart(self, *args, **kwargs) -> cq.Workplane:
        return cq.Workplane("XY")

    @staticmethod
    def selectUpMostFace(project) -> cq.Workplane:

        if project.all() == []:
            return project
        else:
            return project.faces(">Z").workplane()

    @staticmethod
    def selectDownMostFace(project) -> cq.Workplane:

        if project.all() == []:
            return project
        else:
            return project.faces("<Z").workplane()


class BodyTube3DBuilder(Part3DBuilder):

    "A class to build a cylinder or a hollow cylinder if thickness is not zero."

    def create_BodyTube(self, wp: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
        """
        Create cylinder geometry (outer minus inner) on the given workplane.
        Returns a Workplane object with the BodyTube solid positioned at the given workplane.
        """        
        # delegate to primitives
        return create_cylinder(wp, height, radius, thickness)

    def addPart(self, project: cq.Workplane, length: float, diameter: float, thickness: float) -> cq.Workplane:
        """
        Adds the cylinder to the topmost face of the provided project.
        Uses create_BodyTube to build the geometry and then adds it to the project.
        """
        wp = self.selectUpMostFace(project)
        radius = diameter / 2.0

        cyl = self.create_BodyTube(wp, length, radius, thickness)

        project = project.add(cyl)

        return project
    
class Transition3DBuilder(Part3DBuilder):

    "A class to build (hollow) rocket transitions."

    def create_Transition(self, wp: cq.Workplane, height: float, radius1: float, radius2: float, thickness: float) -> cq.Workplane:
        """
        Create transition geometry (outer minus inner) on the given workplane.
        Returns a Workplane object with the transition solid positioned at the given workplane.
        """
        return create_transition(wp, height, radius1, radius2, thickness)

    def addPart(self, project: cq.Workplane, length: float, bottom_diameter: float, top_diameter: float, thickness: float) -> cq.Workplane:
        """
        Arguments:
            project(:cq.Workplane:): current project.
            height(:float:): height of the transition.
            radius1(:float:): radius of the upper part of the transition.
            radius2(:float:): radius of the lower part of the transition.
            thickness(:float:): thickness of the transition.

        Returns:
            project(:cq.Workplane:): the project with an added transition on the up most plane coaxial with the z-axis.
        """
        wp = self.selectUpMostFace(project)
        bottom_radius = bottom_diameter / 2.0
        top_radius = top_diameter / 2.0

        transition = self.create_Transition(wp, length, bottom_radius, top_radius, thickness)

        project = project.add(transition)
        
        return project

class NoseCone3DBuilder(Part3DBuilder):

    "A class to build (hollow) NoseCones"

    def create_NoseCone(self, wp: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
        """
        Create nose cone geometry on the given workplane.
        Returns a Workplane object with the NoseCone solid positioned with base at the given workplane.
        """
        return create_cone(wp, height, radius, thickness)

    def addPart(self, project: cq.Workplane, length: float, diameter: float, thickness: float) -> cq.Workplane:
        """
        Arguments:
            project(:cq.Workplane:): current project.
            height(:float:): height of the cone.
            radius(:float:): base radius of the cone.
            thickness(:float:): thickness of the cone.

        Returns:
            project(:cq.Workplane:): the project with an added cone on the up most plane coaxial with the z-axis.
        """
        wp = self.selectUpMostFace(project)
        radius = diameter / 2.0

        cone = self.create_NoseCone(wp, length, radius, thickness)

        project = project.add(cone)

        return project
    
class Fins3DBuilder(Part3DBuilder):
    "A class to build fin sets"

    def create_FinSet(self, wp: cq.Workplane, count: int, root_chord: float, tip_chord: float, span: float, sweep: float, position: float, thickness: float, body_diameter: float, z_BodyTube: float) -> cq.Workplane:
        """
        Create Fin Set geometry on the given workplane.
        Returns a Workplane object with the FinSet solid positioned with base at the given workplane.
        """
        body_radius = body_diameter / 2.0
    
        local_wp = cq.Workplane("XY")
        fin = create_trapezoidal_fin(local_wp, root_chord, tip_chord, span, sweep, thickness)
        fin = fin.translate((body_radius, 0, position + z_BodyTube))

        finset = None
        for i in range(count):
            angle_deg = i * 360.0 / count
            f = fin.rotate((0, 0, 0), (0, 0, 1), angle_deg)

            if finset is None:
                finset = f
            else:
                finset = finset.union(f)

        if finset is None:
            return cq.Workplane("XY")

        return finset
    
    def addPart(self, project: cq.Workplane, count: int, root_chord: float, tip_chord:float,
                span: float, sweep: float, position: float, thickness: float, body_diameter: float, z_position: float = 0) -> cq.Workplane:
        """
        Arguments:
            project(:cq.Workplane:): current project.

        Returns:
            project(:cq.Workplane:): the project with added fins on the ¿¿WHERE??.
        """
        # Create finset at origin
        finset = self.create_FinSet(None, count, root_chord, tip_chord, span, sweep, position, thickness, body_diameter, z_position)
        
        project = project.add(finset)

        return project

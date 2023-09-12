import cadquery as cq
from abc import ABC, abstractclassmethod

class PartBuilder(ABC):

    @abstractclassmethod
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


class CylinderBuilder(PartBuilder):

    "A class to build hollow cylinders."

    def addPart(self, project: cq.Workplane, height: float, radius: float, thickness: float) -> cq.Workplane:
        """
        Arguments:
            project(:cq.Workplane:): current project.
            height(:float:): height of the cylinder.
            radius(:float:): outer radius of the cylinder.
            thickness(:float:): thickness of the cylinder.

        Returns:
            project(:cq.Workplane:): the project with an added cylinder on the up most plane coaxial with the z-axis.
        """
        
        cylinder = self.selectUpMostFace(project)

        cylinder = cylinder.circle(radius= radius).workplane(offset=height).circle(radius=radius).loft(combine= True)

        project = project.add(cylinder)

        project = self.selectUpMostFace(project)
        
        project = project.hole(diameter= 2*(radius - thickness), depth= height)

        return project
    
class TransitionBuilder(PartBuilder):

    "A class to build hollow rocket transitions."

    def addPart(self, project: cq.Workplane, height: float, radius1: float, radius2: float, thickness: float) -> cq.Workplane:
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
        
        transition = self.selectUpMostFace(project)

        holeTransition = transition.circle(radius2 - thickness).workplane(offset = height).circle(radius1 - thickness).loft(combine=True)

        transition = transition.circle(radius2).workplane(offset = height).circle(radius1).loft(combine=True)

        transition = transition.cut(holeTransition)

        project = project.add(transition)
        
        return project

import cadquery as cq
from .parts import (
    BodyTube3DBuilder,
    Transition3DBuilder,
    NoseCone3DBuilder,
    Fins3DBuilder,
)

class ProjectManager:

    numProjects = 0

    def __init__(self, name = None, project = None) -> None:

        self.name = name
        self.project = project

        self._btbuilder = BodyTube3DBuilder()
        self._tbuilder = Transition3DBuilder()
        self._conebuilder = NoseCone3DBuilder()
        self._fbuilder = Fins3DBuilder()

        # Track the position and diameter of the last body tube added
        self._last_body_diameter = None
        self._last_body_z_position = 0  # Z position where the last body tube sits
        self._last_body_height = 0      # Height of the last body tube

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, projectName): 

        if projectName is None:

            self.numProjects += 1
            self._name =  "project" + str(self.numProjects)
    
        else:

            self._name = projectName
        

    @property
    def project(self): 
        return self._project
    
    @project.setter 
    def project(self, cqProject): 

        if cqProject is None:
            self._project = self.newProject()

        else:
            self._project = cqProject   

    @staticmethod
    def newProject():
        return cq.Workplane("XY")
    
    def addBodyTube(self, length: float, diameter: float, thickness: float) -> None:

        """Adds a (hollow) cylinder to the current project."""

        self.project = self._btbuilder.addPart(project=self.project, length=length, diameter=diameter, thickness=thickness)

        self._last_body_diameter = float(diameter)
        self._last_body_height = float(length)
        # Update Z position: top of the body tube
        self._last_body_z_position = max(s.BoundingBox().zmax for s in self.project.vals())

    def addTransition(self, length: float, bottom_diameter: float, top_diameter: float, thickness: float) -> None: 
        
        """Adds a (hollow) transition to the current project."""

        self.project = self._tbuilder.addPart(project= self.project, length= length, bottom_diameter= bottom_diameter, top_diameter= top_diameter, thickness= thickness)

    def addNoseCone(self, length: float, diameter: float, thickness: float) -> None:

        """Adds a (hollow) NoseCone to the current project."""

        self.project = self._conebuilder.addPart(project= self.project, length= length, diameter= diameter, thickness= thickness)

    def addFinSet(self, count, root_chord, tip_chord, span, sweep, position, thickness, body_diameter=None):
        bd = body_diameter if body_diameter is not None else self._last_body_diameter
        if bd is None:
            raise ValueError("body_diameter not provided and no BodyTube has been added yet")
        
        # Pass the Z position of the base of the last body tube (where fins should attach)
        z_position = self._last_body_z_position - self._last_body_height
        print(z_position)
        print(self._last_body_z_position)
        print(self._last_body_height)
        self.project = self._fbuilder.addPart(self.project, count, root_chord, tip_chord,
                                              span, sweep, position, thickness, body_diameter=bd, z_position=z_position)
    
    def exportProject(self, exportFolderPath: str, format: str): #? Make a new class for exporting projects
        
        path = exportFolderPath + "\\" + self.name + "." + format.lower()
        cq.exporters.export(self.project, path)
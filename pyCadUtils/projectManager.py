import cadquery as cq
from .parts import (
    CylinderBuilder,
    TransitionBuilder,
    ConeBuilder,
)

class ProjectManager:

    numProjects = 0

    def __init__(self, name = None, project = None) -> None:

        self.name = name
        self.project = project

        self._cbuilder = CylinderBuilder()
        self._tbuilder = TransitionBuilder()
        self._conebuilder = ConeBuilder()

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
    
    def addCylinder(self, height: float, radius: float, thickness: float) -> None:

        """Adds a hollow cylinder to the current project."""

        self.project = self._cbuilder.addPart(project=self.project, height=height, radius=radius, thickness=thickness)

    def addTransition(self, height: float, radius1: float, radius2: float, thickness: float) -> None: 
        
        self.project = self._tbuilder.addPart(project= self.project, height= height, radius1= radius1, radius2= radius2, thickness= thickness)

    def addCone(self, height: float, radius: float, thickness: float) -> None:

        self.project = self._conebuilder.addPart(project= self.project, height= height, radius= radius, thickness= thickness)
    
    def exportProject(self, exportFolderPath: str, format: str): #? Make a new class for exporting projects
        
        path = exportFolderPath + "\\" + self.name + "." + format.lower()
        cq.exporters.export(self.project, path)
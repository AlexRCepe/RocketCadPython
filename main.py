from pyCadUtils.projectManager import ProjectManager
from cadquery.vis import show
def main() -> None:

    test_project = ProjectManager(name = "test8")

    test_project.addCylinder(1,0.18,.02)

    test_project.addTransition(0.1,0.15,0.18,.02)

    test_project.addCylinder(0.5,0.15,.02)

    test_project.addCone(0.4,0.15,.02)

    show(test_project.project, alpha=0.7)
    test_project.exportProject(r"C:\Users\jorge\Documents\STAR\STARDUST\RocketCadPython\svgResults", "stl")


if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
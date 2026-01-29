from pyCadUtils.projectManager import ProjectManager
from cadquery.vis import show

def main() -> None:

    test_project = ProjectManager(name = "test8")

    test_project.addBodyTube(length=1,diameter=0.36,thickness=0.02)
    test_project.addFinSet(count=4, root_chord=0.3, tip_chord=0.2, span=0.10, sweep=0.1, position=0.1, thickness=0.02)

    test_project.addTransition(length=0.1,bottom_diameter=0.30,top_diameter=0.36,thickness=0.02)

    test_project.addBodyTube(length=0.5,diameter=0.30,thickness=0.02)
    test_project.addFinSet(count=3, root_chord=0.3, tip_chord=0.2, span=0.10, sweep=0.1, position=0.05, thickness=0.02)

    test_project.addNoseCone(length=0.4,diameter=0.30,thickness=0.02)

    show(test_project.project, alpha=0.5)
    test_project.exportProject(r"C:\Users\jorge\Documents\STAR\STARDUST\RocketCadPython\svgResults", "stl")


if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
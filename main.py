from pyCadUtils.projectManager import ProjectManager

def main() -> None:

    test_project = ProjectManager(name = "test7")

    test_project.addCylinder(10,4,.2)

    test_project.addTransition(2,2,4,.2)

    test_project.addCylinder(4,2,.2)


    test_project.exportProject(r"C:\Users\alexr\Documents\GitHub\RocketCadPython\svgResults", "stl")


if __name__ == "__main__":
    main()
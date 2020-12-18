# Standard library imports
import sys

# osmUtilstemplate imports
from osmUtils import vizzuality
from osmUtils import viewer


def main():
    """
    This runs from the CLI
    """
    if len(sys.argv) > 1:
        vizz = vizzuality.Vizz(sys.argv[1])
        viewer.show(vizz.name)
    else:
        viewer.show('')

if __name__ == "__main__":
    main()

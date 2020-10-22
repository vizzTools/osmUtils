# Standard library imports
import sys

# PyPackage_template imports
from PyPackage_template import vizzuality
from PyPackage_template import viewer


def main():
    if len(sys.argv) > 1:
        vizz = vizzuality.Vizz(sys.argv[1])
        viewer.show(vizz.name)
    else:
        viewer.show('')

if __name__ == "__main__":
    main()

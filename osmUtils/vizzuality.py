
## imports the libraries you have defined in utils.
#from .utils import fecthDesciption


#note: good to have 
#if your classes are going to an API
class Vizz:
    """
    This class ...
    """
    #construct
    def __init__(self, name=None, role=None, desc=False): #self reflects to the instance of the class
        self.name = name
        self.role = role
        self.description = ""
        if desc:
            self.description = getDescription()

    def __repr__(self):
        retunr self.description
        
    def __add__(self, other):

    def getDescription(self):

        if self.name and self.role:
            #fecth employee description from /vizz api endpoint
            description= fecthDesciption(self.name, self.role)
        else:
            " role and name required"
        return desciption

    def changeRole(self, new_role):
        if new_role: self.role = new_role #youre overwriting the role attribute
        print((f"{self.name.title()} is changing from {self.role} to {new_role}"))

        return self

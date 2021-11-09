# Class "pathObject" to represent a path in a WebTemplate 
# including all relevant information about cardinality, suffixes, data type, example values, ...
#
# Jendrik Richter, Jan Janosch Schneider

# TODO:
# Example Creation basierend auf dem rmType der Composition

###########################################################################
# Standard library imports
import types
# Third party imports
# Local application imports

class pathObject:
    id:str = None
    pathString:str = None
    suffixList:list = None
    hasSuffix:bool = None
    hasIndex:bool = None
    maxIndexNumber:int = None
    indexPathDict:dict = None
    isMandatory:bool = None
    rmType:str = None
    datatype:str = None ## TODO
    exampleValueList:list = None ## TODO
    mentionedTerminologiesList:list = None ## TODO
    
    def __init__(self):
        pass

    def __setattr__(self, name, value) -> None:
        # Wird die Suffix-Liste gesetzt, dann wird hasSuffix geupdated
        if name == "suffixList":
            super().__setattr__("suffixList", value)
            if isinstance(value, list) and len(value) > 0:
                super(pathObject, self).__setattr__("hasSuffix", True)
            else:
                super(pathObject, self).__setattr__("hasSuffix", False)
        # Wird der PathString gesetzt, dann wird hasIndex, maxIndexNumber und indexPathDict geupdated
        elif name == "pathString":
            super().__setattr__("pathString", value)
            if "<<index>>" in value:
                super(pathObject, self).__setattr__("hasIndex", True)
                maxIndexNumber = value.count("<<index>>") 
                super(pathObject, self).__setattr__("maxIndexNumber", maxIndexNumber)
                splits = value.split("<<index>>")
                indexPathDict = {}
                for i in range(0, len(splits)-1):
                    if i == 0:
                        indexPath = splits[0].join(splits[:i+1]) + "<<index>>"
                        indexPathDict[indexPath] = None
                    else: 
                        indexPath = "<<index>>".join(splits[:i+1]) + "<<index>>"
                        indexPathDict[indexPath] = None
                super(pathObject, self).__setattr__("indexPathDict", indexPathDict)
            else:
                super(pathObject, self).__setattr__("hasIndex", False)
                super(pathObject, self).__setattr__("maxIndexNumber", 0)
        # Wird keiner der Fälle oben genutzt, dann wird die Variable einfach wie immer gesetzt
        else:
            super().__setattr__(name, value)

    def isEqual(self, pathObject) -> bool:
        if self.id == pathObject.id and self.pathString == pathObject.pathString:
            return True
        else:
            return False

    def contains(self, potentiallyContainedPath) -> bool:
        if self.pathString in potentiallyContainedPath.pathString:
            return True
        else:
            return False

    def print(self) -> str:
        printOutput = (
            f'\tID: \t\t{self.id}\n'
            f'\tPfad: \t\t{self.pathString}\n'
            f'\tPflicht: \t{self.isMandatory}\n'
            f'\tIndexe: \t{self.maxIndexNumber}\n'
            f'\tSuffixe: \t{self.hasSuffix}'
        )
        return str(printOutput)

# Test
#path = pathObject( )
#path.id = "Bericht"
#path.pathString = "Index1<<index>>/Index2<<index>>/Beispiel/Beispiel2/Index3<<index>>"
#print(path.pathString)
#print(path.maxIndexNumber)
#print(path.indexPathList)
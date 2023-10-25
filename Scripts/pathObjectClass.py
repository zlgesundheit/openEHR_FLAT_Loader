# Class "pathObject" to represent a path in a WebTemplate 
# including all relevant information about cardinality, suffixes, data type, ...
#
# Jendrik Richter, Jan Janosch Schneider
#
###########################################################################
# Standard library imports
from decimal import *
# Third party imports
# Local application imports

class pathObject:
    """ """
    id:str = None
    pathString:str = None
    rmType:str = None
    suffixList:list = None
    aql_path: str = None

    max_index:int = None
    has_suffix:bool = None
    has_index:bool = None
    is_mandatory:bool = None
    is_conditional:bool = None

    isMapped:bool = None
    mappedCSVColumn:str = None
    
    index_path_dict:dict = None

    def __init__(self):
        pass

    def __setattr__(self, name, value) -> None:
        """ Setzt weitere Attribute des 'pathObject' abhängig davon, welches Attribut gesetzt wird. """
        # Wird die Suffix-Liste gesetzt, dann wird hasSuffix geupdated
        if name == "suffixList":
            super().__setattr__("suffixList", value)
            if isinstance(value, list) and len(value) > 0:
                super(pathObject, self).__setattr__("hasSuffix", True)
            else:
                super(pathObject, self).__setattr__("hasSuffix", False)
        # Mapped value wird in buildComp gesetzt
        elif name == "mappedCSVColumn":
            super().__setattr__("mappedCSVColumn", value)
            if isinstance(value, str) and len(value) > 0:
                super(pathObject, self).__setattr__("isMapped", True)
            else:
                super(pathObject, self).__setattr__("isMapped", False)
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
                        indexPathDict[indexPath] = None # Hier soll dann rein wie oft der Index vorkommt, zu dem Key indexPath
                    else: 
                        indexPath = "<<index>>".join(splits[:i+1]) + "<<index>>"
                        indexPathDict[indexPath] = None
                super(pathObject, self).__setattr__("indexPathDict", indexPathDict)
            else:
                super(pathObject, self).__setattr__("hasIndex", False)
                super(pathObject, self).__setattr__("maxIndexNumber", 0)
        elif name == "rmType":
            super(pathObject, self).__setattr__("rmType", value)
        # Wird keiner der Fälle oben genutzt, dann wird die Variable einfach wie immer gesetzt
        else:
            super().__setattr__(name, value)

    def isEqual(self, pathObject) -> bool:
        """Vergleicht zwei Pfadobjekte hinsichtlich ID und pathString.

        Args:
          pathObject: 

        Returns:

        """
        if self.id == pathObject.id and self.pathString == pathObject.pathString:
            return True
        else:
            return False

    def contains(self, potentiallyContainedPath) -> bool:
        """Prüft, ob ein Teilstring in einem anderen Teilstring enthalten ist.

        Args:
          potentiallyContainedPath: 

        Returns:

        """
        if self.pathString in potentiallyContainedPath.pathString:
            return True
        else:
            return False

    def __str__(self) -> str:
        """ String Repräsentation der Klasse, welche einige Attribute des 'pathObject' auf der Kommandozeile ausgibt. """
        printOutput = (
            f'\tID: \t\t{self.id}\n'
            f'\tPfad: \t\t{self.pathString}\n'
            f'\tPflicht: \t{self.is_mandatory}\n'
            f'\tIndexe: \t{self.max_index}\n'
            f'\tSuffixe: \t{self.has_suffix}'
        )
        return str(printOutput)
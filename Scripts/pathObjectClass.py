# Class "pathObject" to represent a path in a WebTemplate 
# including all relevant information about cardinality, suffixes, data type, example values, ...
#
# Jendrik Richter, Jan Janosch Schneider
#
###########################################################################
# Standard library imports
from decimal import *
# Third party imports
# Local application imports
from Scripts import exampleGeneratorClass

class pathObject:
    id:str = None
    pathString:str = None
    maxIndexNumber:int = None
    rmType:str = None
    suffixList:list = None 

    hasSuffix:bool = None
    hasIndex:bool = None
    isMandatory:bool = None
    isCondMandatory:bool = None

    isMapped:bool = None
    mappedCSVColumn:str = None
    
    indexPathDict:dict = None
    exampleValueDict:dict = None

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
        # Wenn der rmType gesetzt wird: Setze exampleValueDict mit key: volle pfadnamen ( mit Suffix(en) ) und value: example-wert abhaengig von "rmType" und "type" des Inputs/Suffix
        elif name == "rmType":
            super(pathObject, self).__setattr__("rmType", value)
            exampleValueDict = exampleGeneratorClass.createExampleValueDict(self, value)
            super(pathObject, self).__setattr__("exampleValueDict", exampleValueDict)
        # Wird keiner der Fälle oben genutzt, dann wird die Variable einfach wie immer gesetzt
        else:
            super().__setattr__(name, value)

    def isEqual(self, pathObject) -> bool:
        """ Vergleicht zwei Pfadobjekte hinsichtlich ID und pathString. """
        if self.id == pathObject.id and self.pathString == pathObject.pathString:
            return True
        else:
            return False

    def contains(self, potentiallyContainedPath) -> bool:
        """ Prüft, ob ein Teilstring in einem anderen Teilstring enthalten ist. """
        if self.pathString in potentiallyContainedPath.pathString:
            return True
        else:
            return False

    def __str__(self) -> str:
        """ String Repräsentation der Klasse, welche einige Attribute des 'pathObject' auf der Kommandozeile ausgibt. """
        printOutput = (
            f'\tID: \t\t{self.id}\n'
            f'\tPfad: \t\t{self.pathString}\n'
            f'\tPflicht: \t{self.isMandatory}\n'
            f'\tIndexe: \t{self.maxIndexNumber}\n'
            f'\tSuffixe: \t{self.hasSuffix}'
        )
        return str(printOutput)

# Test

##%
path = pathObject( )
path.pathString = "natars_tzusatz/schmerzerfassung/beliebiges_ereignis:<<index>>/spezifisches_symptom_anzeichen:<<index>>/symptom_krankheitsanzeichen/schmerzstärke:<<index>>"
path.rmType = "DV_DATE_TIME"
print(path.pathString)
print(path.maxIndexNumber)

print(path.exampleValueDict)

print(path)
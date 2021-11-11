# Class "pathObject" to represent a path in a WebTemplate 
# including all relevant information about cardinality, suffixes, data type, example values, ...
#
# Jendrik Richter, Jan Janosch Schneider
#
# TODO: Example Creation basierend auf dem rmType des Pfadobjekts

# Beispiele einfach ersichtlich in WebTemplate_Datatypes in Notes and Testing

# Je nach rmType hat der Pfad inputs mit suffixen oder nicht

# Pfad mit "rmType" =  DV_CODED_TEXT -> Hat "inputs" -> Inputs halten Liste mit "suffix", "type", "terminology" -> Bei "Type" = "CODED_TEXT" gibt es in "inputs" eine "list" -> "list enthaelt "value", "label"
#                                                                                          -> Bei "Type" = "TEXT" ist der Inhalt von "inputs" selbst ein Array mit Elementen mit "suffix", "type","terminology"
# Inputs haelt je nach "type" andere Inhalte

# Pfad mit "rmType" = DV_QUANTITIY hat "inputs" mit Array mit je "suffix" "type" -> mit z.B. |magnitude => "type" = "DECIMAL" und |unit => "type" = CODED_TEXT mit Liste mit "value","label"

# Pfad mit "rmType" = DV_COUNT hat "inputs" mit Array mit "type" z.B. = INTEGER und "validation" = Liste mit "range" die "min", "minOp", "max", "maxOp" angibt. (Z.B. "min":0,"minOp":">=")
# Ähnlich DV_DURATION aber einige Inputs für Jahr,Monat,tag, etc. bis Sekunde

# DV_PROPORTION hat evtl. noch im element "proportionTypes" muesste man in dem Fall mit rausholen in PathExport.py #TODO?

# DV_URI hat "type" = "TEXT"

#DV_BOOLEAN
"""
"inputs": [
    {
        "type": "BOOLEAN"
    }
]
"""

# DV_ORDINAL
"""
"inputs": [
    {
        "type": "CODED_TEXT",
        "list": [
            {
                "value": "at0021",
                "label": "Orindalwert1",
                "localizedLabels": {
                    "de": "Orindalwert1"
                },
                "localizedDescriptions": {
                    "de": "Beschreibung1"
                },
                "ordinal": 1
            },
            {
                "value": "at0022",
                "label": "Ordinalwert2",
                "localizedLabels": {
                    "de": "Ordinalwert2"
                },
                "localizedDescriptions": {
                    "de": "Beschreibung2"
                },
                "ordinal": 2
            },
            {
                "value": "at0023",
                "label": "Ordinalwert3",
                "localizedLabels": {
                    "de": "Ordinalwert3"
                },
                "localizedDescriptions": {
                    "de": "Beschreibung3"
                },
                "ordinal": 3
            }
        ]
    }
]
"""

# ACHTUNG: TODO
# "rmType" = "CODE_PHRASE"
# Keine Inputs aber dafuer 2 Suffixe -> |code und |terminology

# PARTY_PROXY hat "suffix", "type"

# DV_MULTIMEDIA hat 
"""
"inputs": [
    {
        "type": "TEXT"
    }
]
"""

# DV_IDENTIFIER hat "suffix", "type"

# Bei Dates gibts drei Möglichkeiten: DATETIME, DATE und TIME
# Pfad mit "rmType" = DV_DATE_TIME hat "inputs" mit Array mit "type" z.B. = DATETIME und "validation" z.B. gleich "pattern": "yyyy-mm-ddTHH:MM:SS"
#                     DV_DATE hat "type" = "DATE" und "validation" mit "pattern": "yyyy-mm-dd"
#                                          "TIME" dann "pattern": "HH:MM:SS"

###########################################################################
# Standard library imports
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
    isCondMandatory:bool = None
    rmType:str = None
    exampleValueDict:dict = "Beispiel" # None ## TODO ---> Evtl. als dict mit "Key" = pathString MIT Suffix!!!TODO und "Value" = ExampleValue # TODO buildExampleComp.py kurz umschreiben
    exampleValue = "Beispiel" # -> Holds Quatsch-Value until...

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
            
            # TODO
            exampleValueDict = {}
            # Wenn der rmType gesetzt wird:
            #   - Setze exampleValueDict mit key: volle pfadnamen ( mit Suffix(en) ) und value: example-wert abhaengig von "rmType" und "type" des Inputs/Suffix
            #   - Notizen dazu stehen oben oder im WebTemplate_Datatypes_WebTemplate...
            
            super(pathObject, self).__setattr__("exampleValueDict", exampleValueDict)
            pass
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
"""
path = pathObject( )
path.pathString = "natars_tzusatz/schmerzerfassung/beliebiges_ereignis:<<index>>/spezifisches_symptom_anzeichen:<<index>>/symptom_krankheitsanzeichen/schmerzstärke:<<index>>"
print(path.pathString)
print(path.maxIndexNumber)
for key in path.indexPathDict:
    print("\n")
    print(key)
    print(path.indexPathDict)
#"""
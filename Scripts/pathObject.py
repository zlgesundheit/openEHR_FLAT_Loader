# Class "pathObject" to represent a path in a WebTemplate 
# including all relevant information about cardinality, suffixes, data type, example values, ...
#
# Jendrik Richter, Jan Janosch Schneider
#
# TODO: Example Creation basierend auf dem rmType des Pfadobjekts
# Beispiele einfach ersichtlich in WebTemplate_Datatypes in Notes and Testing
# Je nach rmType hat der Pfad inputs mit suffixen oder nicht

###########################################################################
# Standard library imports
from random import randrange
from sys import maxsize
from decimal import *
import os.path
# Third party imports
from numpy import float32
# Local application imports

def setBoundaryByOperator(boundary, operator, changer):
    final_boundary = None
    if      operator == "=" or operator == "<=" or operator == ">=": final_boundary = boundary
    elif    operator == ">": final_boundary = min + changer
    elif    operator == "<": final_boundary = min - changer
    return final_boundary

def getNumberOfType(number_type):
    if   number_type == "INTEGER":  changer = int(1)
    elif number_type == "DECIMAL":  changer = Decimal(0.1)
    elif number_type == "REAL":     changer = float32(0.01)  # Single Precision Floating-Point needed (32-bit)
    elif number_type == "DOUBLE":   changer = float(0.01)  # Double Precision Floating-Point needed (64-bit)
    else: 
        print ("Folgender Zahlentyp konnte nicht erkannt werden: " + number_type)
        # https://specifications.openehr.org/releases/BASE/latest/foundation_types.html#_integer_class
        raise TypeError
    return changer

def getExampleICObase64encoded():
    workdir = os.getcwd()
    filepath = os.path.join(workdir, "Docs", "DV_Multimedia_Example", "icon_base64_encoded.txt")
    f = open( filepath, "r")
    base64_encoded_example_ico = f.read()
    return base64_encoded_example_ico

def getRandNumberWithOrWithoutValidation(entry, changer):
    if 'validation' in entry:
        if 'min' in entry['validation']['range'] and 'max' in entry['validation']['range']:
            final_lower = setBoundaryByOperator( entry['validation']['range']['min'], entry['validation']['range']['minOp'], changer)
            final_upper = setBoundaryByOperator( entry['validation']['range']['max'], entry['validation']['range']['maxOp'], changer)
            number = randrange(final_lower, final_upper)
        elif 'min' in entry['validation']['range'] and not 'max' in entry['validation']['range']:
            final_lower = setBoundaryByOperator( entry['validation']['range']['min'], entry['validation']['range']['minOp'], changer)
            number = randrange(final_lower, maxsize - changer)
        elif not 'min' in entry['validation']['range'] and 'max' in entry['validation']['range']:
            final_upper = setBoundaryByOperator( entry['validation']['range']['max'], entry['validation']['range']['maxOp'], changer)
            number = randrange(0 + changer, final_upper)
    else:
        number = randrange(changer, changer * 10000)
    return number

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
    exampleValueDict:dict = None # None ## TODO ---> Evtl. als dict mit "Key" = pathString MIT Suffix!!!TODO und "Value" = ExampleValue # TODO buildExampleComp.py kurz umschreiben

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
        # Wenn der rmType gesetzt wird:
        #   - Setze exampleValueDict mit key: volle pfadnamen ( mit Suffix(en) ) und value: example-wert abhaengig von "rmType" und "type" des Inputs/Suffix
        #   - Notizen dazu stehen oben oder im WebTemplate_Datatypes_WebTemplate...
        elif name == "rmType":
            super(pathObject, self).__setattr__("rmType", value)
            
            exampleValueDict = {}
            if value == "DV_TEXT":
                exampleValueDict[self.pathString] = "Beispieltext"
            elif value == "DV_MULTIMEDIA":
                exampleValueDict[self.pathString] = getExampleICObase64encoded()
            elif value == "DV_URI":
                # https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.2
                # Format: \s*
                exampleValueDict[self.pathString] = "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"
            elif value == "DV_EHR_URI":
                # https://specifications.openehr.org/releases/RM/latest/data_types.html#_dv_ehr_uri_class
                exampleValueDict[self.pathString] = "ehr://system_id/ehr_id/top_level_structure_locator/path_inside_top_level_structure"
            elif value == "DV_BOOLEAN":
                exampleValueDict[self.pathString] = True
            elif value == "CODE_PHRASE":
                # https://specifications.openehr.org/releases/RM/latest/data_types.html#_code_phrase_class
                if self.id == "language":
                    exampleValueDict[ self.pathString + "|" + 'code' ] = "de"
                    exampleValueDict[ self.pathString + "|" + 'terminology' ] = "ISO_639-1"
                elif self.id == "territory":
                    exampleValueDict[ self.pathString + "|" + 'code' ] = "DE"
                    exampleValueDict[ self.pathString + "|" + 'terminology' ] = "ISO_3166-1"
                elif self.id == "encoding":
                    exampleValueDict[ self.pathString + "|" + 'code' ] = "UTF-8"
                    exampleValueDict[ self.pathString + "|" + 'terminology' ] = "IANA_character-sets"
                else:
                    exampleValueDict[ self.pathString + "|" + 'code' ] = "1234"
                    exampleValueDict[ self.pathString + "|" + 'terminology' ] = "local"
            elif value == "DV_DATE_TIME":
                # DATETIME String nach ISO 8601
                exampleValueDict[self.pathString] = "1989-11-09T21:20:00+02:00"
            elif value == "DV_DATE":
                exampleValueDict[self.pathString] = "1989-11-09"
            elif value == "DV_TIME":
                exampleValueDict[self.pathString] = "21:20:00"
            elif value == "PARTY_PROXY":
                exampleValueDict[ self.pathString + "|" + 'id' ] = "ID 4321"
                exampleValueDict[ self.pathString + "|" + 'id_scheme' ] = "GENERIC_ID"
                exampleValueDict[ self.pathString + "|" + 'id_namespace' ] = "Namesapce"
                exampleValueDict[ self.pathString + "|" + 'name' ] = "Herbert Composer"
            elif value == "DV_IDENTIFIER":
                exampleValueDict[ self.pathString + "|" + 'id' ] = "ID 1234"
                exampleValueDict[ self.pathString + "|" + 'type' ] = "GENERIC_ID"
                exampleValueDict[ self.pathString + "|" + 'issuer' ] = "Issuer Person"
                exampleValueDict[ self.pathString + "|" + 'assigner' ] = "Assigning Organisation X"
            elif value == "DV_COUNT":
                for entry in self.inputs:
                    # Select number type
                    changer = getNumberOfType(entry['type'])
                    number = getRandNumberWithOrWithoutValidation(entry, changer)
                    exampleValueDict[ self.pathString ] = number
            elif value == "DV_DURATION":
                for entry in self.inputs:
                    # Select number type
                    changer = getNumberOfType(entry['type'])
                    number = getRandNumberWithOrWithoutValidation(entry, changer)
                    exampleValueDict[ self.pathString + "|" + entry['suffix'] ] = number
            elif value == "DV_CODED_TEXT":
                pass # TODO
            # DV_QUANTITY TODO
            # DV_PROPORTION TODO
            # DV_ORDINAL TODO
            # DV_PARSABLE TODO
            else:
                # Wenn der rmType hier nicht vorkam, gab es evtl. neue rmTypes o.ä. ?
                print ("Noch nicht behandelter Fall bei Example-Generation in pathObject.py: " + value)
                #raise some Error TODO
            # ExampleValueDict wird hier im Objekt gesetzt!
            super(pathObject, self).__setattr__("exampleValueDict", exampleValueDict)
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
# Functions to generate example for different rmTypes
#
# Jendrik Richter
#
# TODO: Example Creation basierend auf dem rmType des Pfadobjekts
# Beispiele einfach ersichtlich in WebTemplate_Datatypes in Notes and Testing
# Je nach rmType hat der Pfad inputs mit suffixen oder nicht

###########################################################################

# Generate ExampleValue
# 
# Die Ehrbase wirft Fehler beim Uploaden zu unserem BeispielWebtemplate "WebTemplate_Datatypes" 
# -> Evtl. ist das Tempalte outdated? Aber die EHRBase hat es entgegengenommen und das WebTemplate zurückgegeben. 
# Aber Compositions werden dazu nicht gespeichert.
#
# KDS_Medikationseintrag erzeugt als Minimal-Composition:
#   context/start_time
#   composer|name
#   language|code und language|terminology
#   territory|code und territory|terminology
# WebTemplate_Datatypes erzeugt als Minimal-Composition:
#   time
#   time2
#   subject
#   language
#   encoding

# TODO Every CODED_TEXT can be coded internally (in the template) than the example-values need to be from this set to pass validation by the server at runtime
# This also applies to unit of for example a DV_QUANTITY

# Standard library imports
import os
from random import randrange
from decimal import *

# Third party imports
from numpy import float32
# Local application imports

class exampleGenerator:
    exampleValueDict:dict 

    def __init__(self):
        pass

def create_example_value_dict(self, value):
    example_value_dict = {}
    if value == "DV_TEXT":
        if hasattr(self,'inputs'):
            if 'list' in self.inputs[0]:
                example_value_dict[self.pathString] = self.inputs[0]['list'][0]['value']
            else:
                example_value_dict[self.pathString] = "Beispieltext"
        else:
            example_value_dict[self.pathString] = "Beispieltext"
    elif value == "DV_MULTIMEDIA":
        # Example is a file that is in "DV_Multimedia_Example"-Folder in 0_Docs
        example_value_dict[self.pathString] = get_example_ico_base64encoded()
        example_value_dict[self.pathString + "|" + 'mediatype' ] = "IANA::image/jpeg;base64"
        example_value_dict[self.pathString + "|" + 'size' ] = 90196 # Size of the image
        example_value_dict[self.pathString + "|" + 'alternatetext' ] = "alternatetext" ##<- 
    elif value == "DV_URI":
        # https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.2
        # Format: \s*
        example_value_dict[self.pathString] = "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"
    elif value == "DV_EHR_URI":
        # https://specifications.openehr.org/releases/RM/latest/data_types.html#_dv_ehr_uri_class
        example_value_dict[self.pathString] = "ehr://system_id/ehr_id/top_level_structure_locator/path_inside_top_level_structure"
    elif value == "DV_BOOLEAN":
        example_value_dict[self.pathString] = True
    elif value == "CODE_PHRASE":
        # https://specifications.openehr.org/releases/RM/latest/data_types.html#_code_phrase_class
        if self.id == "language":
            example_value_dict[ self.pathString + "|" + 'code' ] = "de"
            example_value_dict[ self.pathString + "|" + 'terminology' ] = "ISO_639-1"
        elif self.id == "territory":
            example_value_dict[ self.pathString + "|" + 'code' ] = "DE"
            example_value_dict[ self.pathString + "|" + 'terminology' ] = "ISO_3166-1"
        elif self.id == "encoding":
            example_value_dict[ self.pathString + "|" + 'code' ] = "UTF-8"
            example_value_dict[ self.pathString + "|" + 'terminology' ] = "IANA_character-sets"
        else:
            example_value_dict[ self.pathString + "|" + 'code' ] = "1234"
            example_value_dict[ self.pathString + "|" + 'terminology' ] = "local"
    elif value == "DV_DATE_TIME":
        # DATETIME String nach ISO 8601
        example_value_dict[self.pathString] = "1989-11-09T21:20:00+02:00"
    elif value == "DV_DATE":
        example_value_dict[self.pathString] = "1989-11-09"
    elif value == "DV_TIME":
        example_value_dict[self.pathString] = "21:20:00"
    elif value == "PARTY_PROXY":
        example_value_dict[ self.pathString + "|" + 'id' ] = "ID 4321"
        example_value_dict[ self.pathString + "|" + 'id_scheme' ] = "GENERIC_ID"
        example_value_dict[ self.pathString + "|" + 'id_namespace' ] = "Namesapce"
        example_value_dict[ self.pathString + "|" + 'name' ] = "Herbert Composer"
    elif value == "DV_IDENTIFIER":
        example_value_dict[ self.pathString + "|" + 'id' ] = "ID 1234"
        example_value_dict[ self.pathString + "|" + 'type' ] = "GENERIC_ID"
        example_value_dict[ self.pathString + "|" + 'issuer' ] = "Issuer Person"
        example_value_dict[ self.pathString + "|" + 'assigner' ] = "Assigning Organisation X"
    elif value == "DV_COUNT": # TODO
        element = self.inputs[0]
        changer = get_numbertype_format(self.inputs[0]['type'])
        number = get_rand_number_with_validationcheck(element, changer)
        example_value_dict[ self.pathString ] = number
    elif value == "DV_DURATION": #TODO Doing
        # Select number type
        for element in self.inputs:
            changer = get_numbertype_format(element['type'])
            number = get_rand_number_with_validationcheck(element, changer)
            example_value_dict[ self.pathString + "|" + element['suffix'] ] = number
    elif value == "DV_CODED_TEXT":
        if hasattr(self, "inputs"):
            # self.inputs[0] 
            if self.inputs[0]['type'] == "CODED_TEXT":
                #print (self.inputs[0]['terminology'])

                example_value_dict[ self.pathString + "|" + 'value' ] = self.inputs[0]['list'][0]['label']
                example_value_dict[ self.pathString + "|" + 'code' ] = self.inputs[0]['list'][0]['value']
                example_value_dict[ self.pathString + "|" + 'terminology' ] = self.inputs[0]['terminology']

        # Eventuell gibt es auch Fälle, bei denen lokal im WebTemplate keine Terminology vorhanden ist aber hier trotzdem Werte eingetragen werden müssen...

    # DV_QUANTITY TODO
    # DV_PROPORTION TODO # Can be in percent or fraction
    elif value == "DV_PROPORTION":
        example_value_dict[ self.pathString + "|" + 'numerator' ] = "albumine"
        example_value_dict[ self.pathString + "|" + 'denominator' ] = "creatinine"
        example_value_dict[ self.pathString + "|" + 'type' ] = "1" # takes an integer? what do we need to set here, if i want "percent"
    # DV_ORDINAL TODO 
        # |value
        # |code
        # |ordinal
    # DV_PARSABLE (e.g. a JSON)
    elif value == "DV_PARSABLE":
        example_value_dict[ self.pathString + "|" + 'value' ] = "{'attribute':'value'}"
        example_value_dict[ self.pathString + "|" + 'formalism' ] = "json"
    else:
        # rmType nicht behandelt
        # Intervalls: upper/lower
        # What is it with: # PROPORTION_KIND, DV_ABSOLUTE_QUANTITY, DV_SCALE, DV_QUANTIFIED
        print ("Noch nicht behandelter Fall bei Example-Generation in pathObject.py: " + value)
        #raise RuntimeError("Test")

    return example_value_dict

def set_boundary(boundary, operator, changer):
    final_boundary = None
    if      operator == "=" or operator == "<=" or operator == ">=": final_boundary = boundary
    elif    operator == ">": final_boundary = boundary + changer
    elif    operator == "<": final_boundary = boundary - changer
    return final_boundary

def get_numbertype_format(number_type):
    if   number_type == "INTEGER":  changer = int(1) # Integer
    elif number_type == "DECIMAL":  changer = Decimal(1.1) # Double
    elif number_type == "REAL":     changer = float32(1.01)  # Single Precision Floating-Point needed (32-bit)
    elif number_type == "DOUBLE":   changer = float(1.01)  # Double Precision Floating-Point needed (64-bit)
    else: 
        print ("Folgender Zahlentyp konnte nicht erkannt werden: " + number_type)
        # https://specifications.openehr.org/releases/BASE/latest/foundation_types.html#_integer_class
        raise TypeError
    return changer

def get_example_ico_base64encoded():
    workdir = os.getcwd()
    filepath = os.path.join(workdir, "0_Docs", "DV_Multimedia_Example", "icon_base64_encoded.txt")
    f = open( filepath, "r")
    base64_encoded_example_ico = f.read()
    return base64_encoded_example_ico

def get_rand_number_with_validationcheck(entry, changer):
    if 'validation' in entry:
        if 'min' in entry['validation']['range'] and 'max' in entry['validation']['range']:
            final_lower = set_boundary( entry['validation']['range']['min'], entry['validation']['range']['minOp'], changer)
            final_upper = set_boundary( entry['validation']['range']['max'], entry['validation']['range']['maxOp'], changer)
            number = randrange(final_lower, final_upper)
        elif 'min' in entry['validation']['range'] and not 'max' in entry['validation']['range']:
            final_lower = set_boundary( entry['validation']['range']['min'], entry['validation']['range']['minOp'], changer)
            number = randrange(final_lower, 12 - changer)
        elif not 'min' in entry['validation']['range'] and 'max' in entry['validation']['range']:
            final_upper = set_boundary( entry['validation']['range']['max'], entry['validation']['range']['maxOp'], changer)
            number = randrange(0 + changer, final_upper)
    else:
        number = randrange(changer, changer * 10000)
    return number
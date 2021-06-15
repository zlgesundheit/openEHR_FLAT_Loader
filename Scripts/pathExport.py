# -*- coding: utf-8 -*-
###########################################################################
# PATHS from WebTemplate

# Dieses Skript extrahiert FLAT-Pfade aus einem WebTemplate. Das WebTemplate basiert auf dem simSDT-WebTemplate Format der Firma Better, 
# welches sowohl die Better Platform als auch die EHRBase unterstützt. 
# 
# Die EHRBase bietet FLAT-Funktionalitäten unter dem "ecis"-Endpunkt an. - Stand Version 0.16 (beta)
# 
# Die openEHR-Community plant die Übernahme des simSDT-Formats in den Standard. - https://specifications.openehr.org/releases/ITS-REST/Release-1.0.2/simplified_data_template.html
#
# FLAT-PFADE 
# FLAT-Pfade erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
# Feld id enthaelt den Namen des Elements
# MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
# Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix
#
# Output
# Ausgabe ist ein Dictionary mit Pfadnamen als key
# ala dict['Pfadname']['rmType'] und dict['Pfadname']['mandatory']
# mandatory ist 0 oder 1, wobei 1 = Pflichtfeld bedeutet
###########################################################################


# List of Types and their attributes (X indicates that this one is **definitely** handled in this script)
# https://specifications.openehr.org/releases/RM/latest/data_types.html

# 6. Quantity Package
#   DV_ORDERED: Abstract -> CODE_PHRASE, DV_INTERVAL, List of REFERENCE_RANGE
#       DV_INTERVAL:        none
#       REFERENCE_RANGE:    DV_TEXT, DV_INTERVAL
#   X   DV_ORDINAL:         DV_CODED_TEXT, value=Integer  (+|ordinal)
#       DV_SCALE:           DV_CODED_TEXT, value=Real
#   DV_QUANTIFIED: Abstract -> magnitude_status, accuracy
#       DV_AMOUNT:          accuracy_is_percent=Boolean, accuracy=Real
#   X   DV_QUANTITY:        magnitude, unit=CODED_TEXT
#   X   DV_COUNT:           value=magnitude
#       DV_PROPORTION:      numerator, denominator, type
#       PROPORTION_KIND:    ...
#       DV_ABSOLUTE_QUANTITY: accuracy: DV_AMOUNT

# 4. Basic Package
#   DATA_VALUE: Abstract
#   ?   DV_BOOLEAN:         value=Boolean  (maybe like DV_COUNT which would mean "no suffix-Case")
#       DV_STATE:           value=DV_CODED_TEXT, is_terminal
#       DV_IDENTIFIER:      id, ...

# 5. Text Package
#   X   DV_TEXT             value:String
#       TERM_MAPPING        match=char, target=CODE_PHRASE
#   X   CODE_PHRASE         code=code_string, terminology=terminology_id
#   X   DV_CODED_TEXT       value, CODE_PHRASE
#   x   DV_PARAGRAPH        This one is DEPRECATED, DV_TEXT (which is markdown formatted) is used instead

# 7. Date Time Package
#       DV_TEMPORAL         accuracy=DV_DUTRATION --> Specialised temporal variant of DV_ABSOLUTE_QUANTITY whose diff type is DV_DURATION.
#   ?   DV_DATE             value=String -> ISO8601 date string         (Structure like DV_COUNT?)
#   ?   DV_TIME             value=String -> ISO8601 time string         (Structure like DV_COUNT?)
#   X   DV_DATE_TIME        value=String -> ISO8601 date/time string    
#   ?   DV_DURATION         value=String -> ISO8601 duration string, including described deviations to support negative values and weeks.   (Structure like DV_COUNT?)

# 8. Time_specification Package
#   DV_TIME_SPECIFICATIONS  Abstract
#       DV_PERIODIC_TIME_SPECIFICATION  --> Specifies periodic points in time, linked to the calendar (phase-linked), or a real world repeating event, such as breakfast (event-linked). Based on the HL7v3 data types PIVL<T> and EIVL<T>. Used in therapeutic prescriptions, expressed as INSTRUCTIONs in the openEHR model.
#       DV_GENERAL_TIME_SPECIFICATION   --> Specifies points in time in a general syntax. Based on the HL7v3 GTS data type.

# 9. Encapsulated Package
#   DV_ENCAPSULATED     Abstract -> Common Metadata -> CODE_PHRASE for charset and language
#       DV_MULTIMEDIA:      media_type=CODE_PHRASE, size: Integer
#       DV_PARSABLE:        value=String, formalism=String

# 10. Uri Package
#       DV_URI              value=String        --> A reference to an object which structurally conforms to the Universal Resource Identifier (URI) RFC-3986 standard
#       DV_EHR_URI                              --> A DV_EHR_URI is a DV_URI which has the scheme name 'ehr', and which can only reference items in EHRs.

###########################################################################
# Standard library imports
import json
import os
from collections import defaultdict
import traceback #debug
# Third party imports
# Local application imports

indent = "    "

def addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath):
    # Pflichtelement
    if element['min'] == 1 and element['max'] == 1:
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "1"  }
    # Pflichtelement das >1 beliebig of vorkommen kann d.h. mit Index
    elif element['max'] == -1 and element['min'] == 1:
        suffixPath += "<<index>>"
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "1"  }
    # Nicht Pflicht beliebig oft d.h. mit Index
    elif element['max'] == -1 and element['min'] == 0:
        suffixPath += "<<index>>"
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "0"  }
    # Nicht Pflicht
    else:
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "0"  }
    return pathDict

def goLow(parentPath, pathDict, children):
    self = children
    for element in self:
            # Fuer jeden Eintrag die ID an den Pfad anhaengen und tiefer gehen # Falls Kardinalitaet mehrfacheintraege zulaesst (Max: -1) dann <<index>>
            if element['max'] == -1:
                selfPath = parentPath + '/' + element['id'] + '<<index>>'
            else:
                selfPath = parentPath + '/' + element['id']

            # Falls Element "children" hat goLow(er)
            childArr = []
            for key in element:
                childArr.append(key)
            if 'children' in childArr:
                pathDict = goLow(selfPath, pathDict, element['children'])

            # Falls Element "Inputs" hat -> Gehe jedes Inputs-Element durch und speichere Pfade
            elif 'inputs' in childArr:
                for inputElement in element['inputs']:
                    # Unterscheidung nach Aufbau statt nach rmType, um alles abzufangen und auch bei Aenderungen oder neuen Datentypen funktional zu bleiben 
                    keysOfInputsElement = []
                    for key in inputElement:
                        keysOfInputsElement.append(key)

                    # Falls DV_CODED_TEXT -> CODED_TEXT + |terminology
                    # +list 
                    # +suffix 
                    # +terminology
                    if ('list' in keysOfInputsElement and 'suffix' in keysOfInputsElement and 'terminology' in keysOfInputsElement) or (element['rmType'] == "DV_CODED_TEXT"):
                        # Suffix |value
                        suffixPath = parentPath + '/' + element['id'] + '|value'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |code
                        suffixPath = parentPath + '/' + element['id'] + '|code'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix | terminology
                        suffixPath = parentPath + '/' + element['id'] + '|terminology'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_QUANTITY
                    # +suffix 
                    # +list 
                    # -terminology
                    elif ('suffix' in keysOfInputsElement and 'list' in keysOfInputsElement and 'terminology' not in keysOfInputsElement ) or (element['rmType'] == "DV_QUANTITY"):
                        # Suffix |magnitude
                        suffixPath = parentPath + '/' + element['id'] + '|magnitude'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |unit
                        suffixPath = parentPath + '/' + element['id'] + '|unit'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_ORDINAL -> CODED_TEXT + |ordinal
                    # + list 
                    # -suffix
                    elif ('list' in keysOfInputsElement and 'suffix' not in keysOfInputsElement) or (element['rmType'] == "DV_ORDINAL"):
                        # Suffix |value
                        suffixPath = parentPath + '/' + element['id'] + '|value'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |code
                        suffixPath = parentPath + '/' + element['id'] + '|code'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |ordinal
                        suffixPath = parentPath + '/' + element['id'] + '|ordinal'
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_COUNT
                    # -suffix 
                    # -list
                    # +type=Integer
                    elif ('list' not in keysOfInputsElement and 'suffix' not in keysOfInputsElement and inputElement['type'] == 'INTEGER') or (element['rmType'] == "DV_COUNT"):
                        suffixPath = parentPath + '/' + element['id'] + "|value"
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_TEXT, DV_DATE_TIME -> kein Suffix
                    # -list 
                    # -suffix 
                    # -type = Integer
                    elif ('list' not in keysOfInputsElement and 'suffix' not in keysOfInputsElement and not inputElement['type'] == 'INTEGER') or (element['rmType'] == "DV_TEXT" or element['rmType'] == "DV_DATE_TIME"):
                        suffixPath = parentPath + '/' + element['id']
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls PARTY_PROXY -> |id , |id_scheme , |id_namespace , |name
                    # +suffix 
                    # -list
                    elif ('suffix' in keysOfInputsElement and 'list' not in keysOfInputsElement) or (element['rmType'] == "PARTY_PROXY"):
                        suffixPath = parentPath + '/' + element['id'] + '|' + inputElement['suffix']
                        pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath)

            # Wenn CODE_PHRASE -> |code und |terminology
            # -children 
            # -inputs
            # -list
            # -suffix
            elif ('children' not in childArr and 'inputs' not in childArr) or (element['rmType'] == "CODE_PHRASE"):
                keyCode = selfPath + '|code'
                keyTerm = selfPath + '|terminology'
                pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, keyTerm)
                pathDict = addPathAndSetRmTypeAndMandatory(pathDict, element, keyCode)

    return pathDict

def getPathsFromWebTemplate(workdir, templateName):
    try:
        # Greife auf WebTemplate zu
        filePath = os.path.join(workdir, 'IntermFiles', templateName +'_WebTemplate.json')
        if os.path.isfile(filePath):
            path = ''
            pathDict = defaultdict(list)
            try:
                # Lese WebTemplate ein
                webTemp = open(filePath, "r", encoding='utf-8').read()
                webTemp = json.loads(webTemp)

                # Durchlaufe den Baum
                path = webTemp['tree']['id']
                pathDict = goLow(path, pathDict, webTemp['tree']['children'])

                ## TODO Hier sind noch ein paar die doppelt hinzugefügt werden! Hier weitermachen TODO
                print ( indent + "Anzahl extrahierter Pfade: " + str( len(pathDict) ) )
                for path in pathDict:
                    #print (path)
                    #print (pathDict[path])
                    #print ("")
                    pass

            except Exception as e:
                print(indent + templateName + "_Webtemplate ist fehlerhaft." + str(e))
                print (indent + str(e))
                traceback.print_exc()
                raise SystemExit
        else:
            raise Exception(templateName + "_WebTemplate ist nicht vorhanden.")
    except Exception as e:
        print (indent + str(e))
        raise SystemExit

    return pathDict
# -*- coding: utf-8 -*-
###########################################################################
# Export PATHS from WebTemplate

# Dieses Skript extrahiert FLAT-Pfade aus einem WebTemplate. Das WebTemplate basiert auf dem simSDT-WebTemplate Format der Firma Better, 
# welches sowohl die Better Platform als auch die EHRBase unterstützt. 
# Die EHRBase bietet FLAT-Funktionalitäten unter dem "ecis"-Endpunkt an. - Stand Version 0.16 (beta)
# Die openEHR-Community plant die Übernahme des simSDT-Formats in den Standard. - https://specifications.openehr.org/releases/ITS-REST/Release-1.0.2/simplified_data_template.html
#
# FLAT-PFADE 
# - FLAT-Pfade erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
# - Feld id enthaelt den Namen des Elements
# - MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
# - Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix
#
# Output
# - Ausgabe ist ein Array von Pfadobjekten (siehe pathObject.py)
# 
# List of openEHR-Types
# https://specifications.openehr.org/releases/RM/latest/data_types.html
#
# TODOs:
# TODO Es wäre gut auch die Validation-Angaben mitzuschleppen. Bei Elementen, die diese haben. 
# TODO Zu jedem Pfad sollte im Pfadobjekt ein valides Beispiel angelegt werden -> Zu händeln hier
###########################################################################

# Standard library imports
import traceback #debug
import sys
import os
# Third party imports
# Local application imports
from Scripts import pathObjectClass

indent = "\t"

############################### Main ###############################

def main(webTemp, templateName):
    print ("PathExport is running:")

    pathArray = []
    try:
        path = webTemp['tree']['id']
        pathIsMandatoryFlag = True 

        # Durchlaufe den Baum
        pathArray = goLow(path, pathArray, pathIsMandatoryFlag, webTemp['tree']['children'])

        # Gib some Output
        print ( indent + "Anzahl extrahierter Pfade: " + str( len(pathArray) ) )
    except Exception as e:
        print(indent + templateName + "_Webtemplate ist fehlerhaft.")
        #print (indent + str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

    print(indent + "Extracted FLAT-Paths from the WebTemplate")
    return pathArray

############################### Methods ###############################

# Rekursiv den Baum durchlaufen
def goLow(parentPath, pathArray, pathIsMandatoryFlag, children):
    self = children

    for element in self:
        # Achtung: Bei jedem Element wieder neue die parentFlag holen, sonst bleibt die Flag nach einem Nicht-Pflichtelement False!
        localMandatoryFlag = pathIsMandatoryFlag

        # Pfad zum aktuellen Element -> Bei (Max: -1) Mehrfacheintraege zulaessig dann :<<index>> im Pfad
        if element['max'] == -1:# or (element['max'] > 1 and element['max'] > element['min']):
            suffixPath = parentPath + '/' + element['id'] + ':<<index>>'
        else:
            suffixPath = parentPath + '/' + element['id']

        # Checken ob wir weiterhin auf einem Pflichtpfad sind
        if element['min'] != 1:
            localMandatoryFlag = False

        # Bei weiteren 'children' tiefer gehen    
        if 'children' in element:
            pathArray = goLow(suffixPath, pathArray, localMandatoryFlag, element['children'])
        
        # Falls Element Inputs hat oder weder Inputs noch Children, dann ist es ein Blatt
        elif 'inputs' in element or element['rmType'] == "CODE_PHRASE":
            # Pfad-Objekt anlegen
            path = pathObjectClass.pathObject()

            path.id = element['id']
            path.pathString = suffixPath
            if 'inputs' in element: # Bei CODE_PHRASE keine inputs -> 2 Suffixe mit Text
                path.inputs = element['inputs']
            path.rmType = element['rmType']
            # Ganzer Pfad ist Pflicht (traegt true oder false ein)
            path.isMandatory = localMandatoryFlag
            # Bedingt Pflicht (nur wenn das Element existiert)
            if not localMandatoryFlag and element['min'] == 1:
                path.isCondMandatory = True

            case4 = ["DV_TEXT", "DV_BOOLEAN", "DV_URI", "DV_EHR_URI", "DV_DATE_TIME", "DV_DATE", "DV_TIME"]

            # Case 1: PARTY_PROXY -> id, id_scheme, id_namespace, name
            if (element['rmType'] == "PARTY_PROXY"):
                path.suffixList = ['id','id_scheme','id_namespace','name']
            # Case 2: DV_IDENTIFIER -> id, type, issuer, assigner
            elif (element['rmType'] == "DV_IDENTIFIER"):
                path.suffixList = ['id','type','issuer','assigner']
            # Case 3: DV_QUANTITY
            elif (element['rmType'] == "DV_QUANTITY"):
                path.suffixList = ['magnitude','unit']
            # Case 4: DV_TEXT, DV_BOOLEAN, DV_URI, DV_EHR_URI,DV_DATE_TIME, DV_DATE, DV_TIME -> No Suffix
            elif element['rmType'] in case4:
                path.suffixList = []
            # Case 5: DV_MULTIMEDIA -> none + mediatype + alternatetext + size
            elif element['rmType'] == "DV_MULTIMEDIA":
                path.suffixList = ['','mediatype','alternatetext','size']
            # Case 6: DV_PROPORTION -> numerator, denominator, type
            elif element['rmType'] == "DV_PROPORTION":
                path.suffixList = ['numerator','denominator','type']
            # Case 7: CODE_PHRASE
            elif (element['rmType'] == "CODE_PHRASE"):
                path.suffixList = ['code','terminology']
            # Case 8: DV_COUNT
            elif (element['rmType'] == "DV_COUNT"):
                path.suffixList = ['value']
            # Case 9: DV_ORDINAL
            elif (element['rmType'] == "DV_ORDINAL"):
                path.suffixList = ['value','code','ordinal']
            # Case 10: DV_CODED_TEXT 
            elif (element['rmType'] == "DV_CODED_TEXT"):
                path.suffixList = ['value','code','terminology']
            # Case 11: DV_PARSABLE -> value, formalism
            elif (element['rmType'] == "DV_PARSABLE"):
                path.suffixList = ['value','formalism']
            # Case 12: DV_DURATION -> year,month,day,week,hour,minute,second	
            elif (element['rmType'] == "DV_DURATION"):
                path.suffixList = []         

            pathArray.append(path)

    return pathArray

if __name__ == '__main__':
    main()
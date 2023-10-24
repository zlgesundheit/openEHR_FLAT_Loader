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
from Scripts import util

indent = "\t"

############################### Main ###############################

def main(webTemp, templateName):
    """

    Args:
      webTemp: param templateName:
      templateName: 

    Returns:

    """
    print ("PathExport is running:")

    pathArray = []
    try:
        path = webTemp['tree']['id']
        pathIsMandatoryFlag = True 

        # Durchlaufe den Baum
        pathArray = traverse_tree_recursive(path, pathArray, pathIsMandatoryFlag, webTemp['tree']['children'])

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
def traverse_tree_recursive(parentPath, pathArray, pathIsMandatoryFlag, children):
    """

    Args:
      parentPath: param pathArray:
      pathIsMandatoryFlag: param children:
      pathArray: 
      children: 

    Returns:

    """
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
            pathArray = traverse_tree_recursive(suffixPath, pathArray, localMandatoryFlag, element['children'])
        
        # Falls Element Inputs hat oder weder Inputs noch Children, dann ist es ein Blatt
        elif 'inputs' in element or element['rmType'] == "CODE_PHRASE":
            # Pfad-Objekt anlegen
            path = pathObjectClass.pathObject()

            path.id = element['id']
            path.path_string = suffixPath
            path.aql_path = element['aqlPath']
            if 'inputs' in element: # Bei CODE_PHRASE keine inputs -> 2 Suffixe mit Text
                path.inputs = element['inputs']
            path.rmtype = element['rmType']
            # Ganzer Pfad ist Pflicht (traegt true oder false ein)
            path.is_mandatory = localMandatoryFlag
            # Bedingt Pflicht (nur wenn das Element existiert)
            if not localMandatoryFlag and element['min'] == 1:
                path.is_conditional = True

            case4 = ["DV_TEXT", "DV_BOOLEAN", "DV_URI", "DV_EHR_URI", "DV_DATE_TIME", "DV_DATE", "DV_TIME"]

            # Case 1: PARTY_PROXY -> id, id_scheme, id_namespace, name
            if (element['rmType'] == "PARTY_PROXY"):
                path.suffix_list = ['id','id_scheme','id_namespace','name']
            # Case 2: DV_IDENTIFIER -> id, type, issuer, assigner
            elif (element['rmType'] == "DV_IDENTIFIER"):
                path.suffix_list = ['id','type','issuer','assigner']
            # Case 3: DV_QUANTITY
            elif (element['rmType'] == "DV_QUANTITY"):
                path.suffix_list = ['magnitude','unit']
            # Case 4: DV_TEXT, DV_BOOLEAN, DV_URI, DV_EHR_URI,DV_DATE_TIME, DV_DATE, DV_TIME -> No Suffix
            elif element['rmType'] in case4:
                path.suffix_list = []
            # Case 5: DV_MULTIMEDIA -> none + mediatype + alternatetext + size
            elif element['rmType'] == "DV_MULTIMEDIA":
                path.suffix_list = ['','mediatype','alternatetext','size']
            # Case 6: DV_PROPORTION -> numerator, denominator, type
            elif element['rmType'] == "DV_PROPORTION":
                path.suffix_list = ['numerator','denominator','type']
            # Case 7: CODE_PHRASE
            elif (element['rmType'] == "CODE_PHRASE"):
                path.suffix_list = ['code','terminology']
            # Case 8: DV_COUNT
            elif (element['rmType'] == "DV_COUNT"):
                path.suffix_list = ['value']
            # Case 9: DV_ORDINAL
            elif (element['rmType'] == "DV_ORDINAL"):
                path.suffix_list = ['value','code','ordinal']
            # Case 10: DV_CODED_TEXT 
            elif (element['rmType'] == "DV_CODED_TEXT"):
                path.suffix_list = ['value','code','terminology']
            # Case 11: DV_PARSABLE -> value, formalism
            elif (element['rmType'] == "DV_PARSABLE"):
                path.suffix_list = ['value','formalism']
            # Case 12: DV_DURATION -> year,month,day,week,hour,minute,second	
            elif (element['rmType'] == "DV_DURATION"):
                path.suffix_list = []         

            pathArray.append(path)

    return pathArray

def map_aql_path_and_id_of_path_object(list_of_path_objects, aql_path_of_element):
    """

    Args:
      list_of_path_objects: param aql_path_of_element:
      aql_path_of_element: 

    Returns:

    """
    for path_object in list_of_path_objects:
        assert isinstance(path_object, pathObjectClass.pathObject), ("Make sure you pass a list of path_objects in "
                                                          "map_aql_path_and_id_of_path_object")
        if util.remove_and_statements(path_object.aql_path)  == aql_path_of_element:
            return path_object.id
    return None

if __name__ == '__main__':
    main()
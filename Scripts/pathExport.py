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
# - FLAT-Pfade erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
# - Feld id enthaelt den Namen des Elements
# - MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
# - Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix
#
# Output
# - Ausgabe ist ein Dictionary mit Pfadnamen als key ala dict['Pfadname']['rmType'] und dict['Pfadname']['mandatory']
# - mandatory ist 0 oder 1, wobei 1 = Pflichtfeld bedeutet
###########################################################################

# List of Types
# https://specifications.openehr.org/releases/RM/latest/data_types.html

# Notes are here: https://pad.gwdg.de/nGok78r6SCK58rlZttKOAw?both

# TODO
# Es wäre gut auch die Validation-Angaben mitzuschleppen. Bei Elementen, die diese haben. 

###########################################################################
# Standard library imports
from collections import defaultdict
import traceback #debug
# Third party imports
# Local application imports
from Scripts import pathObject

indent = "    "
case4 = ["DV_TEXT", "DV_BOOLEAN", "DV_URI", "DV_EHR_URI", "DV_DATE_TIME", "DV_DATE", "DV_TIME"]

############################### Main ###############################

def main(webTemp, templateName):

    pathDict = defaultdict(list)

    pathArray = []
    try:
        # Old Code
        path = webTemp['tree']['id']
        parentMandatoryChain = ""
        pathIsMandatoryFlag = True

        # New Code
        # Ein Pfad wird immer an einem Blatt erstellt... wie geht man vorher mit Min/Max-Angaben o.ä um? 
        # Pflichtpfad kann man mitschleppen -> wird false sobald ein Element kommt, dass nicht Pflicht ist
        # Oder speichert man alle Elemente und macht an Blätter einen Marker, um nur die als Pfade zu nutzen und bei dem Rest nur die Infos zu haben?

        # Durchlaufe den Baum
        pathDict, pathArray = goLow(path, pathDict, pathArray, pathIsMandatoryFlag, webTemp['tree']['children'])

        for path in pathArray:
            print("\n" + path.print())

        # Gib some Output
        print ( indent + "Anzahl extrahierter Pfade: " + str( len(pathDict) ) )

        print ( indent + "Anzahl extrahierter Pfade im Pfad-Objekt Array!: " + str( len(pathArray) ) )
    except Exception as e:
        print(indent + templateName + "_Webtemplate ist fehlerhaft.")
        print (indent + str(e))
        traceback.print_exc()
        raise SystemExit

    return pathDict  ## muss beim neuen code dann das pathArray returnen und dieses muss bei mappingGen und BuildComp richtig verwendet werden

############################### Methods ###############################

# Rekursiv den Baum durchlaufen
def goLow(parentPath, pathDict, pathArray, pathIsMandatoryFlag, children):
    self = children

    for element in self:
        print (element['id'])
        print ("\n")
        # Pfad zum aktuellen Element -> Falls Kardinalitaet Mehrfacheintraege zulaesst (Max: -1) dann <<index>>
        if element['max'] == -1:
            suffixPath = parentPath + '/' + element['id'] + ':<<index>>'
        else:
            suffixPath = parentPath + '/' + element['id']

        # Checken ob wir weiterhin auf einem Pflichtpfad sind
        if element['min'] is 1 and element['max'] is 1:
            pathIsMandatoryFlag = False

        # Bei weiteren 'children' tiefer gehen    
        if 'children' in element:
            pathDict, pathArray = goLow(suffixPath, pathDict, pathArray, pathIsMandatoryFlag, element['children'])
        
        # Falls Element Inputs hat oder weder Inputs noch Children, dann ist es ein Blatt
        elif 'inputs' in element or element['rmType'] == "CODE_PHRASE":
            # Pfad-Objekt anlegen
            path = pathObject.pathObject()

            path.id = element['id']
            path.pathString = suffixPath
            path.isMandatory = pathIsMandatoryFlag
            path.datatype = element['rmType']
            
            """
            # TODO Überdenken: Wir speichern nur ganze Pfade, nicht den Weg dahin. Der Index steht noch im Pfad..Was ausdenken -> evtl. den boolean hier rausnehmen und beim ersetzen der indexe in den Pfaden händeln
            hasIndex:bool = None
            
            # TODO
            exampleValueList:list = None
            Element hat rmType zu dem in den Inputs der Datentype angegeben ist.
            DV_CODED_TEXT hat man eine Liste von CODED_TEXT mit Angabe von terminologie, value und Label
            DV_COUNT hat als Input INTEGER evtl. mit Angabe von min/max im element --> Min/Max Element gilt hier fuer den Value und nicht die Kardinalität!?
            DV_DATE_TIME hat als Input einen DATETIME-Wert
            --> Große IF-Abfrage und dann befuellen mit Beispielwerten abhängig vom type des Inputs

            # TODO haengt mit Beispielen zusammen? Mit For schleife alle elemente hinzufuegen die in der Liste der Inputs sind / oder so
            mentionedTerminologiesList:list = None
            """

            # Case 1: PARTY_PROXY -> id, id_scheme, id_namespace, name
            if (element['rmType'] == "PARTY_PROXY"):
                path.hasSuffix = True
                path.suffixList = ['id','id_scheme','id_namespace','name']

            # Case 2: DV_IDENTIFIER -> id, type, issuer, assigner
            elif (element['rmType'] == "DV_IDENTIFIER"):
                path.hasSuffix = True
                path.suffixList = ['id','type','issuer','assigner']

            # Case 3: DV_QUANTITY
            elif (element['rmType'] == "DV_QUANTITY"):
                suffixes = ['magnitude','unit']

            # Case 4: DV_TEXT, DV_BOOLEAN, DV_URI, DV_EHR_URI,DV_DATE_TIME, DV_DATE, DV_TIME -> No Suffix
            elif element['rmType'] in case4:
                # No Suffix
                suffixes = ['']

            # Case 5: DV_MULTIMEDIA -> none + mediatype + alternatetext + size
            elif element['rmType'] == "DV_MULTIMEDIA":
                # Suffixes
                suffixes = ['','mediatype','alternatetext','size']

            # Case 6: DV_PROPORTION -> numerator, denominator, type
            elif element['rmType'] == "DV_PROPORTION":
                suffixes = ['numerator','denominator','type']

            # Case 7 is below in the else-Part because there are no "inputs" present

            # Case 8: DV_COUNT
            elif (element['rmType'] == "DV_COUNT"):
                suffixes = ['value']

            # Case 9: DV_ORDINAL
            elif (element['rmType'] == "DV_ORDINAL"):
                suffixes = ['value','code','ordinal']

            # Case 10: DV_CODED_TEXT 
            elif (element['rmType'] == "DV_CODED_TEXT"):
                suffixes = ['value','code','terminology']

            # Case 11: DV_PARSABLE -> value, formalism
            elif (element['rmType'] == "DV_PARSABLE"):
                suffixes = ['value','formalism']

            # Case 12: DV_DURATION -> year,month,day,week,hour,minute,second	
            elif (element['rmType'] == "DV_DURATION"):
                suffixes = ['year','month','day','week','hour','minute','second']

            # Case 7: CODE_PHRASE
            elif (element['rmType'] == "CODE_PHRASE"):
                suffixes = ['code','terminology']

            pathArray.append(path)

    return pathDict, pathArray

if __name__ == '__main__':
    main()
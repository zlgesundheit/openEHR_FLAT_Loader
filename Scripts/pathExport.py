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
# FLAT-PFADE erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
# Feld id enthaelt den Namen des Elements
# MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
# Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix
###########################################################################

# Standard library imports
import json
import os
from collections import defaultdict
import traceback #debug
# Third party imports
# Local application imports

indent = "    "

def addRmTypeAndMandatory(pathDict, element, suffixPath):
    if element['min'] == 1 and element['max'] == 1:
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "1"  }
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

            # Falls Element "Inputs" hat -> speichere Pfade
            elif 'inputs' in childArr:
                for inputElement in element['inputs']:
                    # Erzeuge ein Array mit den Keys der Elmente der Kinder von 'Input'
                    childArr = []
                    for key in inputElement:
                        childArr.append(key)

                    # Falls DV_CODED_TEXT
                    if 'suffix' in childArr and element['rmType'] == "DV_CODED_TEXT":
                        # Suffix |code
                        suffixPath = parentPath + '/' + element['id'] + '|code'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |value
                        suffixPath = parentPath + '/' + element['id'] + '|value'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix | terminology
                        suffixPath = parentPath + '/' + element['id'] + '|terminology'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_ORDINAL
                    elif 'list' in childArr and element['rmType'] == "DV_ORDINAL":
                        # Suffix |code
                        suffixPath = parentPath + '/' + element['id'] + '|code'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |value
                        suffixPath = parentPath + '/' + element['id'] + '|value'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)
                        # Suffix |ordinal
                        suffixPath = parentPath + '/' + element['id'] + '|ordinal'
                        addRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls DV_TEXT, DATETIME, INTEGER
                    elif element['rmType'] == "DV_TEXT" or element['rmType'] == "DV_DATE_TIME" or element['rmType'] == "DV_COUNT":
                        suffixPath = parentPath + '/' + element['id']
                        addRmTypeAndMandatory(pathDict, element, suffixPath)

                    # Falls Suffixe da, aber sonst trifft nichts zu -> Zu jedem Suffix den Pfad mit |suffix hinzufügen -> Bsp. Party Proxy mit suffixen
                    elif 'suffix' in childArr:
                        suffixPath = parentPath + '/' + element['id'] + '|' + inputElement['suffix']
                        addRmTypeAndMandatory(pathDict, element, suffixPath)

            # Wenn Element weder "children" noch "inputs" hat --> LANGUAGE TERRITORY -> Bsp. Party Proxy ohne suffixe
            elif not 'children' in childArr and not 'inputs' in childArr:
                keyCode = selfPath + '|code'
                keyTerm = selfPath + '|terminology'
                addRmTypeAndMandatory(pathDict, element, keyTerm)
                addRmTypeAndMandatory(pathDict, element, keyCode)

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
                for path in pathDict:
                    print (path)
                    print (pathDict[path])
                    print ("")
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
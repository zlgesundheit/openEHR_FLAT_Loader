# -*- coding: utf-8 -*-
############################### DEV: PATHS from WebTemplate
# Notes:
# Pfad-Teile stehen im Feld id
# Nachfolgende Pfad-Teile bis zu einem Blatt stehen in children

# Suffixe
  # Jeder Suffix ist ein eigenes Feld mit Pfad

  # Blätter mit nur einem Input haben manchmal Suffix
  # Inputs haben oft Suffix-Angaben die mit |suffix and den Pfad angehängt werden

# Achtung! Suffixe können in Listen sein. In dem Fall Liste durchgehen und Pfade rausschreiben TODO
# Pflichtangabe mit rausschreiben
# Ordentliches Dictionary mit Pfadname, Pflichtangabe, Datentyp

# Kardinalität:
  # Pflicht felder haben min=max=1
  # Felder mit <<index>> haben min:0 max -1 !
    # Wenn ein Element/Pfad ein Pflichtpfad ist, werden sie einer Liste/Array hinzugefuegt, die alle Pflichtpfade enthaelt

# Standard library imports
import json
import os
from collections import defaultdict
import traceback #debug
# Third party imports
# Local application imports

indent = "    "

global mandatoryPathArr
mandatoryPathArr = []

# Add Path-Parts of full Paths as Mandatory Elements
def addToMandatoryPathsArr(path):
    global mandatoryPathArr
    mandatoryPathArr.append(path)

def addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath):
    pathDict[suffixPath].append(element['rmType'])
    if selfPath in mandatoryPathArr:
        pathDict[suffixPath].append("mandatory")
    return pathDict

def goLow(parentPath, pathDict, children):
  global mandatoryPathArr
  self = children
  for element in self:
        # Fuer jeden Eintrag den Pfad erweitern
        # Falls Kardinalitaet mehrfacheintraege zulaesst (Max: -1) dann <<index>>
        if str(element['max']) == str(-1):
            selfPath = parentPath + '/' + element['id'] + '<<index>>'
        else:
            selfPath = parentPath + '/' + element['id']
        # Falls Element ein Pflichtelement ist füge des der Pflichtelement-Liste hinzu
        if element['min'] == 1 and element['max'] == 1:
            addToMandatoryPathsArr(selfPath)
        # Array der Elemente der Kinder
        childArr = []
        for key in element:
            childArr.append(key)
        # Falls Element Kinder hat goLow
        if 'children' in childArr:
            pathDict = goLow(selfPath, pathDict, element['children'])
        # Falls Element Inputs hat, speichere Pfad fuer jeden Suffix
        elif 'inputs' in childArr:
            # Fuer jeden Suffix in inputs speichere den Pfad mit Suffix, sonst wenn keiner da ist ohne suffix, oder falls der rmType DV_Ordinal ist gehe durch die Liste an Werten, oder wenn es ein DV_CODED_TEXT ist speichere noch |value und |terminology zum Code
            for inputElement in element['inputs']:
                # Erzeuge ein Array mit den Keys der Elmente der Kinder von 'Input'
                childArr = []
                for key in inputElement:
                    childArr.append(key)
                # Falls der rmType DV_CODED_TEXT ist, dann gibt es zwar ein 'suffix' in den inputs, aber danach folgt eine Liste 'list' mit den moeglichen Eintraegen, die dann |terminology und |value haben!
                if 'suffix' in childArr and element['rmType'] == "DV_CODED_TEXT":
                    # Suffix |code
                    suffixPath = parentPath + '/' + element['id'] + '|code'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                    # Suffix |value
                    suffixPath = parentPath + '/' + element['id'] + '|value'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                    # Suffix | terminology
                    suffixPath = parentPath + '/' + element['id'] + '|terminology'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                # Falls suffixe auffindbar, speichere den bisherhigen Pfad mit der ID und dem Suffix
                if 'suffix' in childArr and not element['rmType'] == "DV_CODED_TEXT" and not element['rmType'] == "DV_ORDINAL":
                    # Alle vorhandenen Suffixe
                    suffixPath = parentPath + '/' + element['id'] + '|' + inputElement['suffix']
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                # Falls Liste in inputs und das ganze Ordinal ist -> Dann hole gib uns die Pfade mit |value , |ordinal , |code 
                elif 'list' in childArr and element['rmType'] == "DV_ORDINAL":
                    # Suffix |code
                    suffixPath = parentPath + '/' + element['id'] + '|code'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                    # Suffix |value
                    suffixPath = parentPath + '/' + element['id'] + '|value'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                    # Suffix |ordinal
                    suffixPath = parentPath + '/' + element['id'] + '|ordinal'
                    addRmTypeAndMandatory(pathDict, selfPath, element, suffixPath)
                # Falls Element Input hat aber keine Suffixe oder Liste enthaelt fuege Pfad hinzu -> Dann steht dort nur der 'type' des Inputs
                elif not 'suffix' in childArr and not element['rmType'] == "DV_CODED_TEXT" and not element['rmType'] == "DV_ORDINAL":
                    # Ohne Suffix # TODO Mandatory?
                    suffixPath = parentPath + '/' + element['id']
                    pathDict[suffixPath].append(element['rmType'])
        # Wenn Element weder Kinder noch inputs hat fuege pfad mit "Standard"-Suffixen hinzu
        else:
            keyCode = selfPath + '|code'
            pathDict[keyCode].append(element['rmType'])
            keyTerm = selfPath + '|terminology'
            pathDict[keyTerm].append(element['rmType'])
            if selfPath in mandatoryPathArr:
                pathDict[keyCode].append(element['rmType'])
                pathDict[keyTerm].append("mandatory")

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

            except Exception as e:
                print(indent + templateName + "_Webtemplate ist fehlerhaft.")
                print (indent + str(e))
                traceback.print_exc()
                raise SystemExit
        else:
            raise Exception(templateName + "_WebTemplate ist nicht vorhanden.")
    except Exception as e:
        print (indent + str(e))
        raise SystemExit

    return pathDict, mandatoryPathArr
#########################################################################
# Build Compositions
# Using Mapping Table from xlsx
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)
#########################################################################
# Standard library imports
import os.path
import json
import warnings
import traceback #debug
import sys
import re
# Third party imports
import pandas as pd
import numpy as np
# import openpyxl
# Local application imports
from Scripts import handleConfig
from Scripts import pathObjectClass

# openpyxl does not support Validation in Excel-Files and sends a warning
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
indent = "    "
workdir = os.getcwd()

############################### Main ###############################

class knownIndex():
    id = None
    realIndex = None
    mappedIndex = None
    indexCounter = None

    def __init__(self, id, indexString):
        self.id = id
        self.realIndex = None
        self.indexString = indexString
        self.indexCounter = [0] * len(indexString)
        pass

def main(config,manualTaskDir,outputDir):
    print(os.linesep + "BuildComp is running.")
    
    # Read CSV as data frame
    csv_dataframe = handleConfig.readCSVasDataFrame(config.inputCSV)

    # Read Excel-File as data frame
    mapTabDF = xlsxAsDataFrame(manualTaskDir,config.templateName)

    resArray = []
    try:
        if mappingIsEmpty(mapTabDF):
            error_msg = "The Mapping is empty (in buildComp.py)"
            raise Exception(error_msg)

        elif not mappingIsEmpty(mapTabDF):

            # Fuer jede Row/Zeile in CSV = eine Ressource
            for csvIndex, csvRow in csv_dataframe.iterrows():
                # Erstelle ein Dict (pro Zeile) und befuelle es mit allen KEYS + Values
                dict = {}

                # Fuer jeden FLAT_Pfad
                for xlsxIndex, xlsxRow in mapTabDF.iterrows():
                    path = xlsxRow['FLAT-Path (Data field in later composition - if mapped)']
                    indexString = str(xlsxRow['Index(e)'])
                    indexArray = indexString.split(",")
                    indexString = ""
                    for i in range(0, len(indexArray)):
                        indexString = indexString + str(indexArray[i])
                    pathObj = pathObjectClass.pathObject()
                    
                    # Gemappte Spalten auslesen
                    gemappteSpalteAusCSV = mapTabDF['Map CSV-Column to Path (Dropdown-Selector)'][xlsxIndex]
                    metadatumAusSpalteD = mapTabDF['Set Metadata directly (optional)'][xlsxIndex]

                    # Wenn die Zeile gemappt wurde, dann soll sie entsprechend (mit den korrekten Indexen) angelegt werden.
                    if str(metadatumAusSpalteD) != "nan":
                        pathObj.pathString = path
                        pathObj.mappedCSVColumn = metadatumAusSpalteD #Achtung, das setzen der Column-Variable setzt auch den isMapped Bool...

                        # Dict mit KEY = PFAD und VALUE = Value aus der CSV aus Spalte D  
                        if pathObj and pathObj.isMapped:
                            if indexString != "nan":
                                pathString = setIndexesInPath(path, indexString)
                            else:
                                pathString = path
                            dict[pathString] = metadatumAusSpalteD

                    elif str(gemappteSpalteAusCSV) != "nan":
                        pathObj.pathString = path
                        pathObj.mappedCSVColumn = gemappteSpalteAusCSV

                        # Dict mit KEY = PFAD und VALUE = Value aus der CSV aus der gemappten Spalte    
                        if pathObj and pathObj.isMapped and str(csv_dataframe[ pathObj.mappedCSVColumn ][csvIndex]) != "nan":

                            if indexString != "nan":
                                pathString = setIndexesInPath(path, indexString)
                            else:
                                pathString = path

                            dict[pathString] = csv_dataframe[ pathObj.mappedCSVColumn ][csvIndex]

                    else:
                        pass

                # Add Dict to Array of these Dicts
                resArray.append(dict)
        # Dict Building is done
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

    # Erstellte Compositions im Output-Ordner speichern
    storeDictArrayAsRes(outputDir, resArray, config.templateName)

    print(indent + "buildComp finished.\n")

    return resArray

############################### Methods ###############################

def setIndexesInPath(path, indexes):
    for i in range(0, len(indexes)):
        path = path.replace("<<index>>", str(indexes[i]), 1)
    return path

def storeDictArrayAsRes(outputDir,dictArray, templateName):
    '''Dump Dicts as JSON-String in Files'''
    anzahl_eintraege = len(dictArray)
    print ("    Erstelle "+ str(anzahl_eintraege) + " Composition-Ressourcen.")
    i = 0
    for res in dictArray:
        filePath = os.path.join(outputDir, templateName + '_resource' + str(i) + ".json" )
        try:
            with open(filePath,"w", encoding = 'UTF-8') as resFile:
                json.dump(res, resFile, default=convert, indent=4, ensure_ascii=False)
            i += 1
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exc())
            raise SystemExit
    print (indent + str(i) + " / " + str(anzahl_eintraege) + f' Ressourcen erstellt und im Ordner "Output" gespeichert.')

def xlsxAsDataFrame(manualTaskDir,templateName):
    '''Read Mapping as Dataframe'''
    xlsxPath = os.path.join(manualTaskDir, templateName + '_MAPPING.xlsx')
    try:
        mapTabDF = pd.read_excel(xlsxPath, "Auto-indexed Mapping", header=0, engine='openpyxl', dtype=str) 
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
    #engine openpyxl not xlrd since xlrd drop support for non-xls-files
    return mapTabDF

def convert(o):
    '''Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)'''
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def mappingIsEmpty(mapTabDF):
    '''Checken ob das Mapping leer ist, also nur "nan"-Eintraege vorhanden sind'''
    empty = True
    # Checken ob CSV-Column (C) leer ist
    for i in mapTabDF['Map CSV-Column to Path (Dropdown-Selector)']:
        if str(i) != "nan":
            empty = False
    # Wenn C leer war, dann noch Metadaten (D) prüfen
    if empty:
        for i in mapTabDF['Set Metadata directly (optional)']:
            if str(i) != "nan":
                empty = False
    return empty

if __name__ == '__main__':
    main()
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

class indexKombi():
    realIndex = None
    mappedIndex = None
    counter = {}
    counter[0] = 0
    counter[1] = 0
    counter[2] = 0
    counter[3] = 0
    counter[4] = 0

    def __init__(self):
        self.realIndex = None
        self.mappedIndex = None
        self.counter = {}
        self.counter[0] = 0
        self.counter[1] = 0
        self.counter[2] = 0
        self.counter[3] = 0
        self.counter[4] = 0
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
                dict_of_known_indexKombis = {}

                # Fuer jeden FLAT_Pfad
                for xlsxIndex, xlsxRow in mapTabDF.iterrows():
                    path = xlsxRow['FLAT-Path (Data field in later composition - if mapped)']
                    indexArrayString = str(xlsxRow['Index(e)'])
                    pathObj = pathObjectClass.pathObject()
                    
                    # Gemappte Spalten auslesen
                    gemappteSpalteAusCSV = mapTabDF['Map CSV-Column to Path (Dropdown-Selector)'][xlsxIndex]
                    metadatumAusSpalteD = mapTabDF['Set Metadata directly (optional)'][xlsxIndex]

                    # Test mit pathObject
                    if str(metadatumAusSpalteD) != "nan":
                        pathObj.pathString = path
                        pathObj.mappedCSVColumn = metadatumAusSpalteD #Achtung, das setzen der Column-Variable setzt auch den isMapped Bool...

                        # Dict mit KEY = PFAD und VALUE = Value aus der CSV aus der gemappten Spalte    
                        if pathObj and pathObj.isMapped:
                            pathString, dict_of_known_indexKombis = makePathStringWithIndexes(path, indexArrayString, dict_of_known_indexKombis)
                            dict[pathString] = metadatumAusSpalteD

                    elif str(gemappteSpalteAusCSV) != "nan":
                        pathObj.pathString = path
                        pathObj.mappedCSVColumn = gemappteSpalteAusCSV

                        # Dict mit KEY = PFAD und VALUE = Value aus der CSV aus der gemappten Spalte    
                        if pathObj and pathObj.isMapped and str(csv_dataframe[ pathObj.mappedCSVColumn ][csvIndex]) != "nan":
                            pathString, dict_of_known_indexKombis = makePathStringWithIndexes(path, indexArrayString, dict_of_known_indexKombis)
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

def makePathStringWithIndexes(path, indexArrayString, dict_of_known_indexKombis):
    ####################################################################################################################################
    # AD-hoc haessliche Index-Ersetzung aus buildMapping hier ruebergebaut in BuildComp
    # Was passiert hier:
    # Zu einem Pfad steht eine Index-Kombination in Spalte B -> z.B: 0,1,0   
    # (Wenn Pfad mit Index 0,0,0 nicht gesetzt ist, ist in der endgültigen Ressource der Pfad mit 0,1,0 der Pfad mit Indexen 0,0,0 <- Keine Luecken in den Zaehlern.)
    # (Wenn dann Pfad 0,2,0 dazu kommt, dann wird der entsprechend Pfad 0,1,0)
    # Wie?
    # Pro Index-Kombi wird ein Eintrag in einem Dict{} mit KEY = IndexKombi(aka "010") und VALUE = indexKombi-Objekt mit Attributen .realIndex und .counter
    # If Pfad (z.B. 010) schon bekannt, wird der zu verwendende Index aus dem Dict aus dem Objekt ausgelesen.
    # Else der Pfad noch nicht bekannt, 
    #       werden die Indexe für die schon bekannten Teilpfade ausgelesen, ist der schon bekannt, dann wird der bekannte genommen, sonst hochgezaehlt
    #       am Ende wird mit den "korrekten" Indexen die <<index>> Vorkommen im Pfad ersetzt (von links nach rechts immer der nächste mit dem Wert aus dem IndexString z.B: "010")

    # Probleme:
    # pfad1<<index>> und pfad2/pfad<<index>> haben die selbe Index_ID (Beide z.B. 0) -> die 0 bezieht sich aber auf verschiedene Indexeintraege
    # Evtl. das ganze nicht in dict mit KEY = IndexId speichern sondern in dict mit KEY = indexPath <- das wird erstellt, wenn man in Pfadobjekt einen Pfad setzt. 
    # TODO Pfadobjekte nutzen und das ganze pro? indexPath machen... Noch ein Dict mit KEY = IndexPfadString und VALUE = indexPath

    maxIndexNumber = None
    if indexArrayString != "nan":
        # String hat Format i,j,k -> umbauen zu ijk um es als id und key zu nutzen
        indexArray = indexArrayString.split(",")
        indexArrayString = ""
        for i in range(0, len(indexArray)):
            indexArrayString = indexArrayString + str(indexArray[i])
        maxIndexNumber = len(indexArray)
        realIndex = None
        # Index noch nicht bekannt
        if not indexArrayString in dict_of_known_indexKombis:
            # Für einen Index -> Muss nur dieser hochgezaehlt werden
            if maxIndexNumber == 1:

                einstellige_index_id = str(indexArrayString[0])
                realIndex = getRealIndexForMappedIndex(dict_of_known_indexKombis, einstellige_index_id)

                path = setRealIndexesInPath(path, realIndex)

                """
                print (path)
                print (indexArrayString)
                print ("MappedIndex (Obj): ", dict_of_known_indexKombis[indexArrayString].mappedIndex)
                print ("Real Index (Obj): ", dict_of_known_indexKombis[indexArrayString].realIndex)
                print ("Counter (Obj): ", dict_of_known_indexKombis[indexArrayString].counter)

                print ("Pfad nach Ersetzen: ", path)
                print("\n")
                """


            elif maxIndexNumber == 2:
                # Wenn Teil 1 des indexArraqyStrings in schon bekannt, dann nehme den Wert, sonst erhöhe ihn und nehme den
                einstellige_index_id = str(indexArrayString[0])
                realIndex_Part1 = getRealIndexForMappedIndex(dict_of_known_indexKombis, einstellige_index_id)

                dict_of_known_indexKombis[indexArrayString] = indexKombi()
                dict_of_known_indexKombis[indexArrayString].mappedIndex = indexArrayString
                anzahl_vorhandener_pfade_mit_diesem_index = dict_of_known_indexKombis[indexArrayString].counter[2] #anzahl_pfade_best_anzahl[1]
                dict_of_known_indexKombis[indexArrayString].realIndex   = str(realIndex_Part1) + str(anzahl_vorhandener_pfade_mit_diesem_index)
                dict_of_known_indexKombis[indexArrayString].counter[2] = dict_of_known_indexKombis[indexArrayString].counter[2] + 1

                realIndex = str(dict_of_known_indexKombis[indexArrayString].realIndex)

                path = setRealIndexesInPath(path, realIndex)
            
            elif maxIndexNumber == 3:
                
                # Wenn Teil 1 des indexArraqyStrings in schon bekannt, dann nehme den Wert, sonst erhöhe ihn und nehme den
                einstellige_index_id = str(indexArrayString[0])
                realIndex_Part1 = getRealIndexForMappedIndex(dict_of_known_indexKombis, einstellige_index_id)
                # Wenn Teil 2 schon bekannt
                realIndex_Part2 = getRealIndexForMappedIndex(dict_of_known_indexKombis, einstellige_index_id)
                # dann ist teil 3 neu
                dict_of_known_indexKombis[indexArrayString] = indexKombi()
                dict_of_known_indexKombis[indexArrayString].mappedIndex = indexArrayString
                anzahl_vorhandener_pfade_mit_diesem_index = dict_of_known_indexKombis[indexArrayString].counter[3]
                dict_of_known_indexKombis[indexArrayString].realIndex   = str(realIndex_Part1) + str(realIndex_Part2) + str(anzahl_vorhandener_pfade_mit_diesem_index)
                dict_of_known_indexKombis[indexArrayString].counter[3] = dict_of_known_indexKombis[indexArrayString].counter[3] + 1

                realIndex = str(dict_of_known_indexKombis[indexArrayString].realIndex)

                path = setRealIndexesInPath(path, realIndex)

            elif maxIndexNumber == 4:
                
                # Wenn Teil 1 des indexArraqyStrings in schon bekannt, dann nehme den Wert, sonst erhöhe ihn und nehme den
                einstellige_index_id = str(indexArrayString[0])
                realIndex_Part1 = getRealIndexForMappedIndex(dict_of_known_indexKombis, einstellige_index_id)
                # Wenn Teil 2 schon bekannt
                zweistellige_index_id = str(indexArrayString[0]) + str(indexArrayString[1])
                realIndex_Part2 = getRealIndexForMappedIndex(dict_of_known_indexKombis, zweistellige_index_id)
                # Wenn Teil 3 schon bekannt
                dreistellige_index_id = str(indexArrayString[0]) + str(indexArrayString[1] + str(indexArrayString[2]))
                realIndex_Part3 = getRealIndexForMappedIndex(dict_of_known_indexKombis, dreistellige_index_id)
                # dann ist teil 4 neu
                dict_of_known_indexKombis[indexArrayString] = indexKombi()
                dict_of_known_indexKombis[indexArrayString].mappedIndex = indexArrayString
                anzahl_vorhandener_pfade_mit_diesem_index = dict_of_known_indexKombis[indexArrayString].counter[4]
                dict_of_known_indexKombis[indexArrayString].realIndex   = str(realIndex_Part1) + str(realIndex_Part2) + str(realIndex_Part3) +  str(anzahl_vorhandener_pfade_mit_diesem_index)
                dict_of_known_indexKombis[indexArrayString].counter[4] = dict_of_known_indexKombis[indexArrayString].counter[4] + 1

                realIndex = str(dict_of_known_indexKombis[indexArrayString].realIndex)

                path = setRealIndexesInPath(path, realIndex)
                    
        # Falls Index schon bekannt, dann einfach den bestehenden Wert als Index nehmen
        else:
            realIndex = str(dict_of_known_indexKombis[indexArrayString].realIndex)
            path = setRealIndexesInPath(path, realIndex)

    return path, dict_of_known_indexKombis

def setRealIndexesInPath(path, realIndex):
    for i in range(0, len(realIndex)):
        path = path.replace("<<index>>", str(realIndex[i]), 1)
    return path

def getRealIndexForMappedIndex(dict_of_known_indexKombis, index_id):
    counter_id = len(index_id)
    if index_id in dict_of_known_indexKombis:
        realIndex_Part = dict_of_known_indexKombis[index_id].realIndex
    else:
        dict_of_known_indexKombis[index_id] = indexKombi()
        dict_of_known_indexKombis[index_id].mappedIndex = index_id
        dict_of_known_indexKombis[index_id].realIndex = str(dict_of_known_indexKombis[index_id].counter[counter_id])
        dict_of_known_indexKombis[index_id].counter[counter_id] = dict_of_known_indexKombis[index_id].counter[counter_id] + 1

        realIndex_Part = dict_of_known_indexKombis[index_id].realIndex

    return realIndex_Part

####################################################################################################################################

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
#########################################################################
# Build Compositions
# Using Mapping Table from xlsx
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
#
# Note: We flipped the Mapping from CSV <- FLAT-Path to FLAT-Path <- CSV 
# (left part is fixed in Mapping Table, right side gets "mapped" to it)
# If we need the old code: https://gitlab.gwdg.de/medinfpub/openehr_flat_loader/-/commit/db9222717de557c13c36067b20a6a561bc842e4c
# For changes consider Issue #18: https://gitlab.gwdg.de/medinfpub/openehr_flat_loader/-/issues/18
# 
# Jendrik Richter (UMG)
#########################################################################
# Standard library imports
import os.path
import json
import re
import warnings
import traceback #debug
# Third party imports
import pandas as pd
import numpy as np
# import openpyxl
# Local application imports
from Scripts import configHandler

# openpyxl does not support Validation in Excel-Files and sends a warning
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
indent = "    "
workdir = os.getcwd()

############################### Main ###############################

def main():
    
    print(os.linesep + "Step 3: BuildComp is running.")
    
    # Read Config-Values
    config = configHandler.readConf()
    templateName            = config['DEFAULT']['templateName']
    inputCSV                = config['DEFAULT']['inputCSV']

    # Read CSV as data frame
    dataDF = csvAsDataFrame(inputCSV)

    # Read Excel-File as data frame
    mapTabDF = xlsxAsDataFrame(templateName)
  
    # Init some variables
    columnNames = pd.Index( list(mapTabDF.columns.values) )
    colnr_of_csvcolumn = columnNames.get_loc( key='CSV-Column' )
    highestIndex = getHighestIndexNr(columnNames , colnr_of_csvcolumn)

    # Get rid of "NaN"-Values in mapTabDF['CSV-Column']
    mappedCSVItemsWOnan = [x for x in mapTabDF['CSV-Column'] if pd.isnull(x) == False]

    dictArray = []
    try:
        if mappingIsEmpty(mapTabDF):
            errorMsg = "The Mapping is empty."
            raise Exception(errorMsg)

        elif not mappingIsEmpty(mapTabDF):
            # Fuer jede Row/Zeile in CSV = eine Ressource
            for csvIndex, csvRow in dataDF.iterrows():
                # Erstelle ein Dict (pro Zeile) und befuelle es mit allen KEYS + Values
                dict = {}
                
                # Fuer jeden FLAT_Pfad
                for xlsxIndex, xlsxRow in mapTabDF.iterrows():
                    path = xlsxRow['FLAT-Path']
                    # Falls Path nicht NaN fuege Path und Wert hinzu, sonst naechste Zeile im Pfad-Mapping
                    pattern = re.compile("<<index>>")
                    if pattern.search(path):
                        path = replaceIndexStringWithIndexNumber(path,highestIndex,mapTabDF,xlsxIndex)

                    print (path)
                    # Wenn Mapping in Mapping-File vorhanden dann

                    if str(mapTabDF['CSV-Column'][xlsxIndex]) != "nan":
                        # Erstelle einen Dict-Eintrag mit KEY=PATH und VALUE=WERT in der dem KEY zugeordneten Spalte
                        dict[path] = dataDF[ mapTabDF['CSV-Column'][xlsxIndex] ][csvIndex]

                # Add Dict to Array of these Dicts
                dictArray.append(dict)
        # Dict Building is done

        print(indent + "buildComp finished.")
    except Exception as e:
        print(indent + str(e))
        traceback.print_exc()
        raise SystemExit

    # Store ALL Entrys / Resources as .json-files for later use or upload
    storeDictArrayAsRes(dictArray, templateName)

############################### Methods ###############################

def storeDictArrayAsRes(dictArray, templateName):
    i = 0
    for res in dictArray:
        filePath = os.path.join(workdir, 'Output', templateName + '_resource' + str(i) + ".json" )
        with open(filePath,"w", encoding = 'UTF-8') as resFile:
            json.dump(res, resFile, default=convert, indent=4, ensure_ascii=False)
        i += 1

def xlsxAsDataFrame(templateName):
    xlsxPath = os.path.join(workdir, 'ManualTasks', templateName + '_MAPPING.xlsx')
    mapTabDF = pd.read_excel(xlsxPath, "Mapping CSV2openEHR", header=0, engine='openpyxl', dtype=str) 
    #engine openpyxl not xlrd since xlrd drop support for non-xls-files
    return mapTabDF

def csvAsDataFrame(inputCSV):
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    dataDF = pd.read_csv(csvPath, header=0, delimiter=";")
    return dataDF

# Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def replacenth(string, indexNr, n):
    where = [m.start() for m in re.finditer('<<index>>', string)][n-1]
    before = string[:where]
    after = string[where:]
    after = after.replace('<<index>>', ':'+indexNr, 1)
    newString = before + after
    return newString

def getHighestIndexNr(colNr, colnr_of_hinweis):
    # Get String of the Header left of CSV-Column (e.g. "1.Index")
    biggestIndexHeader = colNr[colnr_of_hinweis-1]
    highestIndex = biggestIndexHeader[0] # Erstes zeichen der x.Index Spalte = hoechster Index --> Nur wenn Indexe existieren!
    return int(highestIndex)

def replaceIndexStringWithIndexNumber(path, highestIndex, mapTabDF, xlsxIndex):
    pattern = re.compile("<<index>>")
    if pattern.search(path):
        n = 1
        while n <= highestIndex:
            # Wenn Index nicht angegeben in Mapping-File dann ist er "nan"
            try:
                if str(mapTabDF[str(n) + '. Index'][xlsxIndex]) != "nan":
                    path = replacenth(path, str(mapTabDF[str(n) + '. Index'][xlsxIndex]), n-1)
                    n += 1
                else:
                    n += 1
                    raise Exception( "Bei Pfad %s in Zeile %d fehlt die Index-Angabe!" % (path, xlsxIndex+2) )
            except Exception as e:
                print(indent + str(e))
                #raise SystemExit
    return path

def mappingIsEmpty(mapTabDF):
    # Checken ob das Mapping leer ist, also nur "nan"-Eintraege vorhanden sind
    empty = True
    for i in mapTabDF['CSV-Column']:
        if str(i) != "nan":
            empty = False
    return empty

if __name__ == '__main__':
    main()
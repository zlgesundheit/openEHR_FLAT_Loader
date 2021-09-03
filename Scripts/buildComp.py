# Build Compositions
# Using Mapping Table from xlsx
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)
# Standard library imports
import os.path
import json
import re
import warnings
# Third party imports
import pandas as pd
import numpy as np
# import openpyxl
# Local application imports

# openpyxl does not support Validation in Excel-Files and sends a warning
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
indent = "    "

# Workaround because Pandas uses some panda data types that are NOT serializable..
# Use like json.dumps(dictArray[0]), default=convert)
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

def replaceIndexStringWithIndexNumber(path, highestIndex, mapTabDF, mapTabRunner):
    pattern = re.compile("<<index>>")
    if pattern.search(path):
        n = 1
        while n <= highestIndex:
            # Wenn Index nicht angegeben in Mapping-File dann ist er "nan"
            try:
                if str(mapTabDF[str(n) + '. Index'][mapTabRunner]) != "nan":
                    path = replacenth(path, str(mapTabDF[str(n) + '. Index'][mapTabRunner]), n-1)
                    n += 1
                else:
                    n += 1
                    raise Exception( "Bei Pfad %s in Zeile %d fehlt die Index-Angabe!" % (path, mapTabRunner+2) )
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

def buildComp(templateName, inputCSV):
    print(os.linesep + "Step 3: BuildComp is running.")
    
    ################################# Read Data from Files #################################
    workdir = os.getcwd()
    # Read CSV as data frame
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    dataDF = pd.read_csv(csvPath, header=0, delimiter=";")
    # Read Excel-File
    xlsxPath = os.path.join(workdir, 'ManualTasks', templateName + '_MAPPING.xlsx')
    mapTabDF = pd.read_excel(xlsxPath, "Mapping CSV2openEHR", header=0, engine='openpyxl', dtype=str) #engine openpyxl not xlrd since xlrd drop support for non-xls-files
  
    colNr = pd.Index( list(mapTabDF.columns.values) )
    colnr_of_csvcolumn = colNr.get_loc( key='CSV-Column' )
    highestIndex = getHighestIndexNr(colNr , colnr_of_csvcolumn)

    try:
        if mappingIsEmpty(mapTabDF):
            errorMsg = "The Mapping is empty."
            raise Exception(errorMsg)
        elif not mappingIsEmpty(mapTabDF):
            dictArray = []
            dataDFRunner = 0
            # Fuer jeden Eintrag / Row in der Quelldaten-CSV -> Jede Zeile = eine Ressource
            for entry in dataDF[ mapTabDF['CSV-Column'][0] ]:
                # Fuer jede Zeile des Mappings erstelle ein Dict und befuelle es mit allen KEYS + Values
                mapTabRunner = 0
                dict = {}
                # Fuer jeden FLAT_Pfad
                for path in mapTabDF['FLAT-Path']:
                    # Falls Path nicht NaN fuege Path und Wert hinzu, sonst naechste Zeile im Pfad-Mapping
                    pattern = re.compile("<<index>>")
                    if pattern.search(path):
                        path = replaceIndexStringWithIndexNumber(path,highestIndex,mapTabDF,mapTabRunner)
                    #try:
                    # Wenn Mapping in Mapping-File vorhanden dann
                    if str(mapTabDF['CSV-Column'][mapTabRunner]) != "nan":
                        # Erstelle einen Dict-Eintrag mit KEY=PATH und VALUE=WERT in der dem KEY zugeordneten Spalte
                        dict[path] = dataDF[ mapTabDF['CSV-Column'][mapTabRunner] ][dataDFRunner]
                    #else:
                    #    raise Exception("Der Pfad %s in Zeile %d wurde nicht gemappt!" % (path, mapTabRunner+2) )
                    #except Exception as e:
                    #    print(indent + str(e))
                        #raise SystemExit
                    mapTabRunner += 1
                # Add Dict to Array of these Dicts
                dictArray.append(dict)
                dataDFRunner += 1
        # Dict Building is done

        #print(dictArray)

        # Store ALL Entrys / Resources as .json-files for later use or upload
        i = 0
        for res in dictArray:
            filePath = os.path.join(workdir, 'Output', templateName + '_resource' + str(i) + ".json" )
            with open(filePath,"w", encoding = 'UTF-8') as resFile:
                json.dump(res, resFile, default=convert, indent=4, ensure_ascii=False)
            i += 1

        print(indent + "buildComp finished.")
    except Exception as e:
        print(indent + str(e))
        raise SystemExit

    answerString = ""
    return answerString

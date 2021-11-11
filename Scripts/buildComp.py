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
# Third party imports
import pandas as pd
import numpy as np
# import openpyxl
# Local application imports

# openpyxl does not support Validation in Excel-Files and sends a warning
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
indent = "    "
workdir = os.getcwd()

############################### Main ###############################

def main(config):
    print(os.linesep + "Step 3: BuildComp is running.")
    
    # Read CSV as data frame
    dataDF = csvAsDataFrame(config.inputCSV)

    # Read Excel-File as data frame
    mapTabDF = xlsxAsDataFrame(config.templateName)

    resArray = []
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

                    # Schaue ob Mapping in Mapping-File eingetragen / vorhanden ist
                    gemappteSpalteAusCSV = mapTabDF['CSV-Column'][xlsxIndex]
                    if str(gemappteSpalteAusCSV) != "nan":
                        # Erstelle einen Dict-Eintrag mit KEY=PATH und VALUE=WERT in der dem KEY zugeordneten Spalte
                        if str(dataDF[ gemappteSpalteAusCSV ][csvIndex]) != "nan":
                            dict[path] = dataDF[ gemappteSpalteAusCSV ][csvIndex]
                        else:
                            pass

                # Add Dict to Array of these Dicts
                resArray.append(dict)
        # Dict Building is done

        print(indent + "buildComp finished.")
    except Exception as e:
        print(indent + str(e))
        traceback.print_exc()
        raise SystemExit

    # Erstellte Compositions im Output-Ordner speichern
    storeDictArrayAsRes(resArray, config.templateName)

    return resArray

############################### Methods ###############################

def storeDictArrayAsRes(dictArray, templateName):
    '''Dump Dicts as JSON-String in Files'''
    i = 0
    for res in dictArray:
        filePath = os.path.join(workdir, 'Output', templateName + '_resource' + str(i) + ".json" )
        with open(filePath,"w", encoding = 'UTF-8') as resFile:
            json.dump(res, resFile, default=convert, indent=4, ensure_ascii=False)
        i += 1
    print (indent + str(i) + f' Ressourcen erstellt und im Ordner "Output" gespeichert. \n')

def xlsxAsDataFrame(templateName):
    '''Read Mapping as Dataframe'''
    xlsxPath = os.path.join(workdir, 'ManualTasks', templateName + '_MAPPING.xlsx')
    mapTabDF = pd.read_excel(xlsxPath, "Auto-indexed Mapping", header=0, engine='openpyxl', dtype=str) 
    #engine openpyxl not xlrd since xlrd drop support for non-xls-files
    return mapTabDF

def csvAsDataFrame(inputCSV):
    '''Read CSV as Dataframe'''
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    dataDF = pd.read_csv(csvPath, header=0, delimiter=";")
    return dataDF

def convert(o):
    '''Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)'''
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def mappingIsEmpty(mapTabDF):
    '''Checken ob das Mapping leer ist, also nur "nan"-Eintraege vorhanden sind'''
    empty = True
    for i in mapTabDF['CSV-Column']:
        if str(i) != "nan":
            empty = False
    return empty

if __name__ == '__main__':
    main()
# Build Compositions
# Using Mapping Table from xlsx
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)

import pandas as pd
import numpy as np
import openpyxl
import re
import json
import os.path

indent = "    "
# Workaround because Pandas uses some panda data types that are NOT serializable..
# Use like json.dumps(dictArray[0]), default=convert
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

def getHighestIndexNr(mapTabDF):
  # Find out what the highest index is --> the first char in the last col left of the column named "Hinweis:" it is!
  colNr = pd.Index( list(mapTabDF.columns.values) )
  nr = colNr.get_loc( key='Hinweis:' )
  # Get String of the Header left of Hinweis
  biggestIndexHeader = colNr[nr-1]
  highestIndex = biggestIndexHeader[0]
  return int(highestIndex)

def convertIndexCols(mapTabDF, highestIndex):
  i = 0
  while i < highestIndex:
    colNr = pd.Index( list(mapTabDF.columns.values) )
    ColName = colNr[2+i]
    mapTabDF = mapTabDF.astype( {ColName:str} )
    i += 1
    return mapTabDF

def buildComp(workdir, templateName, inputCSV):
  print(os.linesep + "Step 3: BuildComp is running.")
  # Read CSV as data frame
  csvPath = os.path.join(workdir, 'Input', inputCSV + '.csv')
  dataDF = pd.read_csv(csvPath, header=0, delimiter=";")

  # Read Excel-File
  xlsxPath = os.path.join(workdir, 'Manual Tasks', templateName + '_MAPPING.xlsx')
  mapTabDF = pd.read_excel(xlsxPath, "Mapping CSV2openEHR", header=0, engine='openpyxl')
  highestIndex = getHighestIndexNr(mapTabDF)
  # Cast Index Columns to String instead of float64
  mapTabDF = convertIndexCols(mapTabDF, highestIndex)

  empty = True
  errorMsg = ""
  # Checken ob das Mapping leer ist, also nur "nan"-Eintraege vorhanden sind
  for i in mapTabDF['FLAT-Path']:
    if str(i) != "nan":
      empty = False

  try:
    if empty:
      errorMsg = "The Mapping is empty."
      raise Exception(errorMsg)
    elif not empty:
      dictArray = []
      dataDFRunner = 0
      # Fuer jeden Eintrag / Row in der Quelldaten-CSV
      for entry in dataDF[ mapTabDF['CSV-Column'][0] ]:
        # Fuer jede Zeile des Mappings erstelle ein Dict und befuelle es mit allen KEYS + Values
        mapTabRunner = 0
        dict = {}
        for path in mapTabDF['FLAT-Path']:
          # Falls Path nicht NaN fuege Path und Wert hinzu, sonst naechste Zeile im Pfad-Mapping
          if (str(path) != "nan"):
            # Falls <<index>> im String enthalten ersetze die Zeichenfolge mit dem Index-Wert aus der Spalte Index (1. Vorkommen mit 1. Index, 2. Vorkommen mit 2. Index)
            pattern = re.compile("<<index>>")
            if pattern.search(path):
              n = 1
              x = mapTabDF[str(n) + '. Index'][mapTabRunner]
              while n <= highestIndex:
                path = replacenth(path, str( int(  float(mapTabDF[str(n) + '. Index'][mapTabRunner]))), n-1)
                n += 1
            # Erstelle einen Dicteintrag mit KEY=PATH und VALUE=WERT in der dem KEY zugeordneten Spalte
            dict[path] = dataDF[ mapTabDF['CSV-Column'][mapTabRunner] ][dataDFRunner]
            mapTabRunner += 1
          else:
            mapTabRunner +=1
        # Add Dict to Array of these Dicts
        dictArray.append(dict)
        dataDFRunner += 1
      # Dict Building is done

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

# Old Code
  #pattern = "<<index>>"
  #path = re.sub(pattern, str(mapTabDF['Index'][mapTabRunner]), path)

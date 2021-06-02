# Build Compositions
# Using Mapping Table from xlsx
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)

import pandas as pd
import numpy as np
import re
import json
import os.path

indent = "    "
# Workaround because Pandas uses some panda data types that are NOT serializable..
# Use like json.dumps(dictArray[0]), default=convert
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def buildComp(workdir, templateName, inputCSV):
  print(os.linesep + "Step 3: BuildComp is running.")
  # Read CSV as data frame
  csvPath = os.path.join(workdir, 'Input', inputCSV + '.csv')
  dataDF = pd.read_csv(csvPath, header=0, delimiter=";")

  # Read Excel-File
  xlsxPath = os.path.join(workdir, 'Manual Tasks', templateName + '_MAPPING.xlsx')
  mapTabDF = pd.read_excel(xlsxPath, "Mapping CSV2openEHR", header=0, usecols=[0,1,2], converters={'Index':str})

  empty = "true"
  # Checken ob das Mapping leer ist, also nur "nan"-Eintraege vorhanden sind
  for i in mapTabDF['FLAT-Path']:
    if str(i) != "nan":
      empty =  "false"

  try:
    if (empty == "true"):
      raise Exception(indent + "The Mapping is empty.")
    else:
      dictArray = []
      dataDFRunner = 0
      # Fuer jeden Eintrag / Row in der Quelldaten-CSV
      for entry in dataDF[ mapTabDF['CSV-Column'][0] ]:
        #print(entry)
        # Fuer jede Zeile des Mappings erstelle ein Dict und befuelle es mit allen KEYS + Values
        mapTabRunner = 0
        dict = {}
        for path in mapTabDF['FLAT-Path']:
          # Falls Path nicht NaN fuege Path und Wert hinzu, sonst naechste Zeile im Pfad-Mapping
          if (str(path) != "nan"):
            # Falls <<index>> im String enthalten ersetze die Zeichenfolge mit dem Index-Wert aus der Spalte Index
            pattern = "<<index>>"
            path = re.sub(pattern, str(mapTabDF['Index'][mapTabRunner]), path)
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
        f = open(filePath,"w")
        f.write(json.dumps(res, default=convert, indent=4))
        i += 1
        f.close()

      print(indent + "buildComp finished.")
  except:
    print(indent + "The Mapping is empty.")

  answerString = ""
  return answerString
# Generate a Mapping List
# Manually map CSV-Columns on FLAT-Paths
#
# Jendrik Richter (UMG)
############################################################
# Standard library imports
import os.path
import re
# Third party imports
import xlsxwriter
import pandas as pd
# Local application imports

indent = "    "

def generateList(workdir, templateName, inputCSV, pathsArray):
  print(os.linesep + "Step 2: MappingListGen is running.")

  # Create Excel-File
  excelPath = os.path.join(workdir, 'Manual Tasks', templateName + '_MAPPING.xlsx')
  workbook = xlsxwriter.Workbook(excelPath)
  worksheetMapping = workbook.add_worksheet('Mapping CSV2openEHR')
  worksheetPaths = workbook.add_worksheet('FLAT_Paths')

  ####### Read CSV and put Items/CSV-Column-Names in sheet 1 in the excel file
  csvPath = os.path.join(workdir, 'Input', inputCSV + '.csv')
  df = pd.read_csv(csvPath, header=0, delimiter=";")

  # Write Path-Values (for Dropdown-List)
  
  worksheetPaths.set_column('A:A', 50)
  worksheetPaths.write('A1', 'FLAT-Path')
  i = 1
  indexArr = []
  for path in pathsArray:
    worksheetPaths.write(i, 0, path)
    # Nach Vorkommen von <<index>> suchen und pro Index eine weitere Index-Spalte hinzufuegen
    pattern = '<<index>>'
    indexList = re.findall(pattern, path)
    indexArr.append( len(indexList) )
    max_value = None
    for num in indexArr:
        if (max_value is None or num > max_value):
            max_value = num
    # Anzahl Pfade, um unten die Laenge der Dropdownauswahl festzulegen        
    numberofPaths = i
    i += 1

  #### Build Mapping Worksheet
  worksheetMapping.write('A1', 'CSV-Column')
  worksheetMapping.write('B1', 'FLAT-Path')
  # Index-Spalten hinzufuegen
  ind = 0
  while ind < max_value:
    worksheetMapping.write(0, ind+2, str(ind + 1) + '. Index' )
    ind += 1
  # ind+2 ter Buchstaben des Alphabets, damit der Eintrag als Header im DataFrame in BuildComp genutzt werden kann
  worksheetMapping.write(chr(ord('A') + ind+2 )+'1' , 'Hinweis:') 
  worksheetMapping.write(1, ind+2 , 'Wählen Sie für jedes Feld einen entsprechenden FLAT-Pfad per Auswahl im Dropdown-Menü')
  worksheetMapping.write(2, ind+2 , 'Bei FLAT-Pfaden mit dem Element "<<index>>" wählen Sie den Index (z.B. für eine best. Messung) beginnend mit 0')
  worksheetMapping.set_column('A:A', 50)
  worksheetMapping.set_column('B:B', 80)
  worksheetMapping.set_column('D:D', 30)
  # Dropdown-Listen hinbzufuegen
  i = 1
  for col in df.columns:
    worksheetMapping.write(i, 0, col)
    worksheetMapping.data_validation('B'+str(i+1), {'validate': 'list','source': '=FLAT_Paths!$A$2:$A$' + str(numberofPaths +1)})
    i += 1

  workbook.close()

  print(indent + "Mapping List is generated.")

  answerString = ""
  return answerString

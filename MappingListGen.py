# Generate a Mapping List
# Manually map CSV-Columns on FLAT-Paths
#
# Jendrik Richter (UMG)

import pandas as pd
import xlsxwriter
import os.path

indent = "    "

def generateList(workdir, templateName, inputCSV, pathsArray):
  print(os.linesep + "Step 2: MappingListGen is running.")

  # Create Excel-File
  excelPath = os.path.join(workdir, 'Manual Tasks', templateName + '_MAPPING.xlsx')
  workbook = xlsxwriter.Workbook(excelPath)

  ####### Read CSV and put Items/CSV-Column-Names in sheet 1 in the excel file
  csvPath = os.path.join(workdir, 'Input', inputCSV + '.csv')
  df = pd.read_csv(csvPath, header=0, delimiter=";")

  worksheet = workbook.add_worksheet('Mapping CSV2openEHR')
  worksheet.write('A1', 'CSV-Column')
  worksheet.write('B1', 'FLAT-Path')
  worksheet.write('C1', 'Index')
  worksheet.write('D1', 'Hinweis:')
  worksheet.write('D2', 'Wählen Sie für jedes Feld einen entsprechenden FLAT-Pfad per Auswahl im Dropdown-Menü')
  worksheet.write('D3', 'Bei FLAT-Pfaden mit dem Element "<<index>>" wählen Sie den Index (z.B. für eine best. Messung) beginnend mit 0')
  worksheet.set_column('A:A', 50)
  worksheet.set_column('B:B', 80)
  worksheet.set_column('D:D', 130)
  ###  Index Spalte hinzufügen
  i = 1
  for col in df.columns:
    worksheet.write(i, 0, col)
    worksheet.data_validation('B'+str(i+1), {'validate': 'list','source': '=FLAT_Paths!$A$2:$A$25'})
    i += 1

  # Write Path-Values (for Dropdown-List)
  worksheet = workbook.add_worksheet('FLAT_Paths')
  worksheet.set_column('A:A', 50)
  worksheet.write('A1', 'FLAT-Path')
  i = 1
  for path in pathsArray:
    worksheet.write(i, 0, path)
    i += 1

  workbook.close()

  print(indent + "Mapping List is generated.")

  answerString = ""
  return answerString
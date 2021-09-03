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

def setTableAppearance(workbook):
    mapping_item_cell_format = workbook.add_format()
    mapping_item_cell_format.set_align('valign')
    mapping_item_cell_format.set_text_wrap()

    header_cell_format = workbook.add_format()
    header_cell_format.set_bg_color('#808080')

    return workbook, header_cell_format, mapping_item_cell_format

def generateList(templateName, inputCSV, pathsArray):
    print(os.linesep + "Step 2: MappingListGen is running.")
    workdir = os.getcwd()
    # Create Excel-File
    excelPath = os.path.join(workdir, 'ManualTasks', templateName + '_MAPPING.xlsx')
    workbook = xlsxwriter.Workbook(excelPath)

    worksheetMapping = workbook.add_worksheet('Mapping CSV2openEHR')
    worksheetPaths = workbook.add_worksheet('FLAT_Paths')
    worksheetCSVPaths = workbook.add_worksheet('CSV_Paths')

    # Set Appearance
    workbook, header_cell_format, mapping_item_cell_format = setTableAppearance(workbook)

    ######################################## Compose FLAT_Paths Worksheet ########################################
    # Write Path-Values AND rmTypes for each path-element
    worksheetPaths.set_column('A:A', 100)
    worksheetPaths.write('A1', 'FLAT-Path', header_cell_format)
    worksheetPaths.set_column('B:B', 60)
    worksheetPaths.write('B1', 'rmType', header_cell_format)
    worksheetPaths.set_column('C:C', 100)
    worksheetPaths.write('C1','Mandatory Paths', header_cell_format)

    # Alle Pfade mit rmType
    j = 1
    nrMandatoryPaths = 0
    indexArr = []
    max_value = None
    for path in pathsArray:
        worksheetPaths.write(j, 0, path)

        # Falls Pflichtfeld dann entsprechend kenntlich machen in Mandatory Spalte i,2 (dict['pfad']['mandatory'] = 1)
        if pathsArray[path]['mandatory'] == str(1):
            worksheetPaths.write(j, 2, "Pflicht (Pfad muss gegebensein, damit die Ressource valide ist!)")
            nrMandatoryPaths += 1
        elif pathsArray[path]['mandatory'] == str(-1):
            worksheetPaths.write(j, 2, "Bedingt Pflicht (Muss gegeben sein, falls übergeordnete Elemente existieren)")

        # rmType ausgeben in rmType-Spalte i,1
        worksheetPaths.write(j, 1, pathsArray[path]['rmType'])

        # Nach Vorkommen von <<index>> suchen und ermitteln wieviele Indexe im Pfad mit den meisten Indexen ist (max number of indexes)
        pattern = '<<index>>'
        indexList = re.findall(pattern, path)
        indexArr.append( len(indexList) )
        for num in indexArr:
            if (max_value is None or num > max_value):
                max_value = num
        # Anzahl Pfade, um unten die Laenge der Dropdownauswahl festzulegen        
        numberofPaths = j
        j += 1

    print( indent + "Anzahl der mindestens zu verwendenden Pfade: " + str(nrMandatoryPaths) )

    ######################################## Compose CSV Worksheet ########################################
    worksheetCSVPaths.set_column('A:A', 100)
    worksheetCSVPaths.write('A1', 'CSV-Column', header_cell_format)
    worksheetCSVPaths.set_column('B:B', 60)
    worksheetCSVPaths.write('B1', 'Example-Value', header_cell_format)

    ####### Read CSV and put Items/CSV-Column-Names in sheet 1 in the excel file
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    df = pd.read_csv(csvPath, header=0, delimiter=";")

    # Add Entrys
    i = 1
    for col in df.columns:
        # Write example values from csv (first row) to column 2 in the Worksheet
        try:
            worksheetCSVPaths.write(i, 1, df[col].iloc[0], mapping_item_cell_format)
        except:
            worksheetCSVPaths.write(i, 1, "NaN")
        # Write CSV-Column Names
        worksheetCSVPaths.write(i, 0, col, mapping_item_cell_format)
        i += 1

    ######################################## Compose Mapping Worksheet ########################################
    #### Build Mapping Worksheet
    worksheetMapping.write('A1', 'FLAT-Path', header_cell_format)
    # Index-Spalten hinzufuegen (Zeile 1 = Flat Paths, Zeile 2+ind = Indexe, Zeile 2+ind+1 = CSV-Item Dropdown)
    ind = 0
    while ind < max_value:
        worksheetMapping.write(0, ind+1, str(ind + 1) + '. Index' , header_cell_format)
        ind += 1
    columnCharFLATpath   = chr(ord('A') + ind + 1)
    columnCharExampleVal = chr(ord('A') + ind + 2)
    worksheetMapping.write( columnCharFLATpath   + '1', 'CSV-Column', header_cell_format) #Buchstabe aus dem Alphabet an Position 1 Spalte +Indexanzahl an Spalten
    worksheetMapping.write( columnCharExampleVal + '1', 'Example-Value', header_cell_format)

    worksheetMapping.set_column('A:A', 100)
    worksheetMapping.set_column('B:B', 15)
    worksheetMapping.set_column('C:C', 50)
    worksheetMapping.set_column('D:D', 25)

    # FLAT Paths in Spalte 1 und Dropdowns in Spalte 3 bzw. Rechts von der letzten Index-Spalte hinzufuegen
    i = 1
    for path in pathsArray:
        worksheetMapping.write(i, 0, path)
        worksheetMapping.data_validation('C'+str(i+1), {'validate': 'list','source': '=CSV_Paths!$A$2:$A$' + str(numberofPaths +1)})
        i += 1

    # Dropdown-Listen hinzufuegen
    i = 1
    for col in df.columns:
        # Write example values from csv (first row) to column 2 in the Worksheet
        try:
            worksheetMapping.write(i, 2+ind, df[col].iloc[0], mapping_item_cell_format)
        except:
            worksheetMapping.write(i, 1, "NaN")
        i += 1

    workbook.close()

    print(indent + "Mapping List is generated.")

    answerString = ""
    return answerString

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

    mapping_item_cell_format = workbook.add_format()
    mapping_item_cell_format.set_align('valign')
    mapping_item_cell_format.set_text_wrap()

    header_cell_format = workbook.add_format()
    header_cell_format.set_bg_color('#808080')

    worksheetMapping = workbook.add_worksheet('Mapping CSV2openEHR')
    worksheetPaths = workbook.add_worksheet('FLAT_Paths')

    ####### Read CSV and put Items/CSV-Column-Names in sheet 1 in the excel file
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    df = pd.read_csv(csvPath, header=0, delimiter=";")

    # Write Path-Values (for Dropdown-List) AND rmTypes for each path-element
    worksheetPaths.set_column('A:A', 100)
    worksheetPaths.write('A1', 'FLAT-Path', header_cell_format)
    worksheetPaths.set_column('B:B', 60)
    worksheetPaths.write('B1', 'rmType', header_cell_format)
    worksheetPaths.set_column('C:C', 100)
    worksheetPaths.write('C1','Mandatory Paths', header_cell_format)

    # Alle Pfade mit rmType
    i = 1
    nrMandatoryPaths = 0
    indexArr = []
    max_value = None
    for path in pathsArray:
        worksheetPaths.write(i, 0, path)

        # Falls Pflichtfeld dann entsprechend kenntlich machen in Mandatory Spalte i,2 (dict['pfad']['mandatory'] = 1)
        if pathsArray[path]['mandatory'] == str(1):
            worksheetPaths.write(i, 2, "Pflicht/Mandatory (Dieser Pfad muss in einer validen Ressource gegeben sein)")
            nrMandatoryPaths += 1
        elif pathsArray[path]['mandatory'] == str(-1):
            worksheetPaths.write(i, 2, "Bedingt Pflicht/Mandatory (Nur wenn vorangehende Elemente existiert)")

        # rmType ausgeben in rmType-Spalte i,1
        worksheetPaths.write(i, 1, pathsArray[path]['rmType'])

        # Nach Vorkommen von <<index>> suchen und ermitteln wieviele Indexe im Pfad mit den meisten Indexen ist (max number of indexes)
        pattern = '<<index>>'
        indexList = re.findall(pattern, path)
        indexArr.append( len(indexList) )
        for num in indexArr:
            if (max_value is None or num > max_value):
                max_value = num
        # Anzahl Pfade, um unten die Laenge der Dropdownauswahl festzulegen        
        numberofPaths = i
        i += 1

    print( indent + "Anzahl der mindestens zu verwendenden Pfade: " + str(nrMandatoryPaths) )

    #### Build Mapping Worksheet
    anzahlFixerSpalten = 3
    worksheetMapping.write('A1', 'CSV-Column', header_cell_format)
    worksheetMapping.write('B1', 'Example-Value', header_cell_format)
    worksheetMapping.write('C1', 'FLAT-Path', header_cell_format)

    worksheetMapping.set_column('A:A', 50)
    worksheetMapping.set_column('B:B', 50)
    worksheetMapping.set_column('C:C', 100)
    worksheetMapping.set_column('D:D', 25)


    # Index-Spalten hinzufuegen
    ind = 0
    while ind < max_value:
        worksheetMapping.write(0, ind+anzahlFixerSpalten, str(ind + 1) + '. Index' , header_cell_format)
        ind += 1
    # ind+anzahlFixerSpalten ter Buchstaben des Alphabets, damit der Eintrag als Header im DataFrame in BuildComp genutzt werden kann
    worksheetMapping.write(chr(ord('A') + ind+anzahlFixerSpalten )+'1' , 'Hinweis:') 
    worksheetMapping.write(1, ind+anzahlFixerSpalten , 'Wählen Sie für jedes Feld einen entsprechenden FLAT-Pfad per Auswahl im Dropdown-Menü')
    worksheetMapping.write(2, ind+anzahlFixerSpalten , 'Bei FLAT-Pfaden mit dem Element "<<index>>" wählen Sie den Index (z.B. für eine best. Messung) beginnend mit 0')

    # Dropdown-Listen hinbzufuegen
    i = 1
    for col in df.columns:
        # In case of NaN Values
        try:
            worksheetMapping.write(i, 1, df[col].iloc[0], mapping_item_cell_format)
        except:
            worksheetMapping.write(i, 1, "NaN")
        # Write CSV-Items in first row (0)
        worksheetMapping.write(i, 0, col, mapping_item_cell_format)
        worksheetMapping.data_validation('C'+str(i+1), {'validate': 'list','source': '=FLAT_Paths!$A$2:$A$' + str(numberofPaths +1)})
        i += 1



    workbook.close()

    print(indent + "Mapping List is generated.")

    answerString = ""
    return answerString

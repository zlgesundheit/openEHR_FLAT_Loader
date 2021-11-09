# Generate a Mapping List
# Manually map CSV-Columns on FLAT-Paths
#
# Jendrik Richter (UMG)
############################################################
# Standard library imports
import os.path
from math import prod
from numpy import number
# Third party imports
import xlsxwriter
import pandas as pd
# Local application imports
from Scripts import pathObject

indent = "\t"
workdir = os.getcwd()

############################### Main ###############################

def main(templateName, inputCSV, pathArray):
    print("MappingListGen is running:")
    
    # Create Excel-File
    excelPath = os.path.join(workdir, 'ManualTasks', templateName + '_MAPPING.xlsx')
    workbook = xlsxwriter.Workbook(excelPath)

    worksheetAutoIndexedMapping = workbook.add_worksheet('Auto-indexed Mapping')
    worksheetPaths = workbook.add_worksheet('FLAT_Paths')
    worksheetCSVPaths = workbook.add_worksheet('CSV_Items')

    # Set Appearance -> Muss man die Worksheets mmit zurueckgeben? TODO
    setAppearanceForAllSheets(workbook, worksheetAutoIndexedMapping, worksheetPaths, worksheetCSVPaths)

    df, numberOfCSVitems = readCSVasDF(inputCSV)

    # Compose CSV_Items Worksheet
    composeCSVitemWorksheet(df, worksheetCSVPaths)
    # Compose FLAT_Path Worksheet
    composeFlatPathsWorksheet(pathArray, worksheetPaths)
    # Compose Auto-indexed Mapping Worksheet
    composeAutoIndexedWS(worksheetAutoIndexedMapping, pathArray, numberOfCSVitems)

    workbook.close()
    print("Generated the (empty) Mapping-Table")

############################### Methods ###############################

def composeAutoIndexedWS(worksheetMapping, pathArray, numberOfCSVitems):
    '''Composes mapping-worksheet based on index-values from userinput.'''

    # add paths + dropdown list
    local_indexPathDict = {}
    list_of_queried_index_elements = []
    row = 1
    for path in pathArray:
        # Falls Path keinen Index 
        if not path.hasIndex:
            # Wenn Suffix dann pro Suffix einen Pfad
            if path.hasSuffix:
                for suffix in path.suffixList:
                    worksheetMapping.write('A'+str(row+1),path.pathString + "|" + suffix)
                    worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})
                    row += 1
            elif not path.hasSuffix:
                worksheetMapping.write('A'+str(row+1),path.pathString)
                worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})
                row += 1
        # Falls Path Index hat
        elif path.hasIndex:   # how to get the index number that shall not be quieried?
            
            # Abfrage von Indexen   (hier werden alle Pfade durchlaufen die mind. einen Index haben und nur einmal gefragt)
            # Wir springen hier von PfadObjekt zu Pfadobjekt. Dadurch muessen wir die erfassten Indexpfadwerte zwischenspeichern 
            # um sie den PFadobjekten hinzufuegen zu koennen, die danach kommen und fuer die kein Input kommt.
            for indexPath in path.indexPathDict:
                path.indexPathDict[indexPath] = []
                if not indexPath in list_of_queried_index_elements:
                    print (f'Wie viele Werte sind zum Element ({indexPath}) vorhanden?')
                    userInput = int(input('Anzahl der Messwerte: '))
                    path.indexPathDict[indexPath].append(userInput)
                    list_of_queried_index_elements.append(indexPath)
                    local_indexPathDict[indexPath] = path.indexPathDict[indexPath]
                else:
                    path.indexPathDict[indexPath] = local_indexPathDict[indexPath]
            
            # Jedes Pfad-Objekt hat nun in path.indexPathDict die Angabe, wie oft das Element vorkommt und zwar als Array mit Wert fuer jeden Index!
            for userInputArray in path.indexPathDict:
                for index in path.indexPathDict[userInputArray]:   
                    # Werden nacheinander die Index-Inputs fuer einen Pfad durchlaufen -> Solange man immer das erste vorkommen ersetzt sollten so alle nacheinander ersetzt werden?
                    realPathString = path.pathString
                    for j in range(0,index):
                        realPathString = realPathString.replace('<<index>>',(str(j)),1)
                        # Wenn Suffix dann pro Suffix einen Pfad
                        if path.hasSuffix:
                            for suffix in path.suffixList:
                                worksheetMapping.write('A'+str(row+1),realPathString + "|" + suffix)
                                worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})
                                row += 1
                        elif not path.hasSuffix:
                            worksheetMapping.write('A'+str(row+1),realPathString)
                            worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})
                            row += 1

            for key in path.indexPathDict:
                print(key)
                print ("=")
                print(path.indexPathDict[key])

def pathContainedInIndexedElement(pathString, indexedElement):
    if indexedElement in pathString:
        return True
    else:
        return False

def readCSVasDF(inputCSV):
    csvPath = os.path.join(workdir, 'Input', 'CSV', inputCSV + '.csv')
    df = pd.read_csv(csvPath, header=0, delimiter=";")
    numberOfCSVitems = len(df.columns)

    return df, numberOfCSVitems

def composeCSVitemWorksheet(df, worksheetCSVPaths):
    i = 1
    for col in df.columns:
        # Write CSV-Column Names
        worksheetCSVPaths.write(i, 0, col)
        # Write Data
        try:
            worksheetCSVPaths.write(i, 1, df[col].iloc[0])
        except:
            worksheetCSVPaths.write(i, 1, "NaN")
        i += 1

def composeFlatPathsWorksheet(pathArray, worksheetPaths):
    j = 1
    nrMandatoryPaths = 0
    for path in pathArray:
        worksheetPaths.write(j, 0, path.pathString)
        worksheetPaths.write(j, 1, path.rmType)
        if path.isMandatory:
            worksheetPaths.write(j, 2, "Pflichtpfad")
            nrMandatoryPaths += 1
        j += 1
        # TODO Bedingt Pflicht angeben (Item ist Pflicht, wenn Parent-Element vorher existiert)
    print( indent + "Anzahl der Pflichtpfade: " + str(nrMandatoryPaths) )

def setAppearanceForAllSheets(workbook, worksheetAutoIndexedMapping, worksheetPaths, worksheetCSVPaths):
    # Allgemein -> TODO Not used atm
    mapping_item_cell_format = workbook.add_format()
    mapping_item_cell_format.set_align('valign')
    mapping_item_cell_format.set_text_wrap()

    header_cell_format = workbook.add_format()
    header_cell_format.set_bg_color('#808080')

    # Flat-Pfad Worksheet
    worksheetPaths.set_column('A:A', 100)
    worksheetPaths.set_column('B:B', 60)
    worksheetPaths.set_column('C:C', 100)
    worksheetPaths.write('A1', 'FLAT-Path', header_cell_format)
    worksheetPaths.write('B1', 'rmType', header_cell_format)
    worksheetPaths.write('C1','Mandatory Paths', header_cell_format)

    # CSV-Items
    worksheetCSVPaths.set_column('A:A', 100)
    worksheetCSVPaths.set_column('B:B', 60)
    worksheetCSVPaths.write('A1', 'CSV-Column', header_cell_format)
    worksheetCSVPaths.write('B1', 'Example-Value', header_cell_format)

    # Mapping
    worksheetAutoIndexedMapping.write('A1', 'FLAT-Path', header_cell_format)
    worksheetAutoIndexedMapping.write('B1', 'CSV-Column', header_cell_format) 
    worksheetAutoIndexedMapping.set_column('A:A', 100)
    worksheetAutoIndexedMapping.set_column('B:B', 50)

if __name__ == '__main__':
    main()
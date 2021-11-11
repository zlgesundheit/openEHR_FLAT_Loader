# Generate a Mapping List
# Manually map CSV-Columns on FLAT-Paths
#
# Jendrik Richter (UMG)
############################################################
# Standard library imports
import os.path
# Third party imports
import xlsxwriter
import pandas as pd
# Local application imports
from Scripts import pathObject

import sys
sys.setrecursionlimit(10000)

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

    # Set Appearance -> TODO Farbliches Hervorheben von Pflichtpfaden o.ä.?
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
    alreadyAddedPath = []
    for path in pathArray:
        # Falls Path keinen Index 
        if not path.hasIndex:
            # Wenn Suffix dann pro Suffix einen Pfad
            if path.hasSuffix:
                for suffix in path.suffixList:
                    addPathWithSuffix(path.pathString, suffix, row, worksheetMapping, numberOfCSVitems)
                    addMandatoryColumnEntry(path, row, worksheetMapping)
                    row += 1
            elif not path.hasSuffix:
                addPathWithoutSuffix(path.pathString, row, worksheetMapping, numberOfCSVitems)
                # Pflichtangabe
                addMandatoryColumnEntry(path, row, worksheetMapping)
                row += 1
        # Falls Path Index hat
        elif path.hasIndex:   # how to get the index number that shall not be quieried?
            # Abfrage von Indexen   (hier werden alle Pfade durchlaufen die mind. einen Index haben und nur einmal gefragt)
            # Wir springen hier von PfadObjekt zu Pfadobjekt. Dadurch muessen wir die erfassten Indexpfadwerte zwischenspeichern 
            # um sie den PFadobjekten hinzufuegen zu koennen, die danach kommen und fuer die kein Input kommt.
            for indexPath in path.indexPathDict:
                if not indexPath in list_of_queried_index_elements:
                    print (f'Wie viele Werte sind zum Element ({indexPath}) vorhanden?')
                    userInput = int(input('Anzahl der Messwerte: '))
                    path.indexPathDict[indexPath] = userInput
                    local_indexPathDict[indexPath] = path.indexPathDict[indexPath]
                    list_of_queried_index_elements.append(indexPath)
                else:
                    path.indexPathDict[indexPath] = local_indexPathDict[indexPath]

            # Jedes Pfad-Objekt hat nun in path.indexPathDict die Angabe, wie oft das Element vorkommt und zwar als Array mit Wert fuer jeden Index!
            indexArray = []
            for key in path.indexPathDict:
                indexArray.append(path.indexPathDict[key])
            path.indexArray = indexArray
        
            if path.maxIndexNumber == 1:
                for indexStellenMaximum in indexArray:
                    for j in range(0,indexStellenMaximum):
                        String_with_0_index = path.pathString.replace('<<index>>',(str(j)))
                        if path.hasSuffix:
                            for suffix in path.suffixList:
                                addPathWithSuffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems)
                                addMandatoryColumnEntry(path, row, worksheetMapping)
                                row += 1
                        elif not path.hasSuffix:
                            addPathWithoutSuffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems)
                            # Pflichtangabe
                            addMandatoryColumnEntry(path, row, worksheetMapping)
                            row += 1
            # Das Problem mit mehreren Indexen (n^m^k etc.) :
            # Permutationen klappen nicht, weil die Maximalwerte der einzelnen Indexstellen dann nicht Beachtung finden
            # Liste von Listen mit validen Kombinationen (n-Laufvariablen die hochzaehlen und an bestehende Listen anfügen...)
            # Array von Laufvariablen das durchlaufen wird war auch irgendwie Mist.
            # Idee: Stückweise Ersetzung im Pfad beginnend von links -> REKURSIV...natürlich
            ## SLOW AND DIRTY weil Python keine Rekursion in For-Schleifen kann.
            ## In Manual schreiben, dass wir nur Pfade mit bis zu 4 Indexen unterstützen :D :D -> Nochmal mit Jan diskutieren TODO
            elif path.maxIndexNumber == 2:
                realPathString = path.pathString
                for j in range(0,indexArray[0]):
                    String_with_1_index_left = realPathString.replace('<<index>>',(str(j)),1)
                    for i in range(0,indexArray[1]):
                        String_with_0_index = String_with_1_index_left.replace('<<index>>',(str(i)),1)
                        if not String_with_0_index in alreadyAddedPath:
                            if path.hasSuffix:
                                for suffix in path.suffixList:
                                    addPathWithSuffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems)
                                    addMandatoryColumnEntry(path, row, worksheetMapping)
                                    row += 1
                            elif not path.hasSuffix:
                                addPathWithoutSuffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems)
                                # Pflichtangabe
                                addMandatoryColumnEntry(path, row, worksheetMapping)
                                row += 1
                            alreadyAddedPath.append(String_with_0_index)
            elif path.maxIndexNumber == 3:
                somePathString = path.pathString
                for j in range(0,indexArray[0]):
                    String_with_2_index_left = somePathString.replace('<<index>>',(str(j)),1)
                    for i in range(0,indexArray[1]):
                        String_with_1_index = String_with_2_index_left.replace('<<index>>',(str(i)),1)
                        for k in range(0,indexArray[2]):
                            String_with_0_index = String_with_1_index.replace('<<index>>',(str(k)),1)
                            if not String_with_0_index in alreadyAddedPath:
                                if path.hasSuffix:
                                    for suffix in path.suffixList:
                                        addPathWithSuffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems)
                                        addMandatoryColumnEntry(path, row, worksheetMapping)
                                        row += 1
                                elif not path.hasSuffix:
                                    addPathWithoutSuffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems)
                                    # Pflichtangabe
                                    addMandatoryColumnEntry(path, row, worksheetMapping)
                                    row += 1
                                alreadyAddedPath.append(String_with_0_index)
            elif path.maxIndexNumber == 4:
                somePathString = path.pathString
                for m in range(0,indexArray[0]):
                    String_with_3_index_left = somePathString.replace('<<index>>',(str(m)),1)
                    for j in range(0,indexArray[1]):
                        String_with_2_index_left = String_with_3_index_left.replace('<<index>>',(str(j)),1)
                        for i in range(0,indexArray[2]):
                            String_with_1_index = String_with_2_index_left.replace('<<index>>',(str(i)),1)
                            for k in range(0,indexArray[3]):
                                String_with_0_index = String_with_1_index.replace('<<index>>',(str(k)),1)
                                if not String_with_0_index in alreadyAddedPath:
                                    if path.hasSuffix:
                                        for suffix in path.suffixList:
                                            addPathWithSuffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems)
                                            addMandatoryColumnEntry(path, row, worksheetMapping)
                                            row += 1
                                    elif not path.hasSuffix:
                                        addPathWithoutSuffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems)
                                        addMandatoryColumnEntry(path, row, worksheetMapping)
                                        row += 1
                                    alreadyAddedPath.append(String_with_0_index)


"""
elif path.maxIndexNumber > 1:
    #[5,3,3] = IndexArray
    resultArray = []
    final_path = setNextIndex(path.pathString, resultArray, indexArray, 0)
"""

def addPathWithSuffix(pathString, suffix, row, worksheetMapping, numberOfCSVitems):
    worksheetMapping.write('A'+str(row+1),pathString + "|" + suffix)
    worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})

def addPathWithoutSuffix(pathString, row, worksheetMapping, numberOfCSVitems):
    worksheetMapping.write('A'+str(row+1),pathString)
    worksheetMapping.data_validation('B'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})

def addMandatoryColumnEntry(path, row, worksheetMapping):
    # Pflichtangabe
    if path.isMandatory:
        worksheetMapping.write('C'+str(row+1),"Pflichtpfad")
    # Bedingt Pflichtelement
    if path.isCondMandatory:
        worksheetMapping.write('C'+str(row+1),"Bedingt Pflichtelement")

def setNextIndex(realPathString, resultArray, indexArray, i):
    if not "<<index>>" in realPathString:
        return realPathString
    for j in range(0, indexArray[i]):
        nuuuuPath = realPathString.replace('<<index>>',(str(j)),1)
        print(nuuuuPath)
        nuuuuPath = setNextIndex(nuuuuPath, resultArray, indexArray, i + 1)

"""
s = iter(pathString.split("<<index>>"))
(next(s) + "".join(str(y)+x for x,y in zip(s,myList)))
"""
""" 
Funktionierende Version die nur daran scheitert, dass Python nicht robust genug ist und die Stacks verwirft und dann None returned.
Das Problem ist das Konstrukt: Zuviele Stacks weil er in der For-Loop die Reku
def foo(step=0):
    for i in range(step, 4):
        print step
        foo(step+1)

def setNextIndex(realPathString, indexArray, i):
    if not "<<index>>" in realPathString:
        return realPathString
    for j in range(0, indexArray[i]):
        nuuuuPath = realPathString.replace('<<index>>',(str(j)),1)
        print(nuuuuPath)
        nuuuuPath = setNextIndex(nuuuuPath, indexArray, i + 1)

tail-calling is certainly not just for lists; any tree structure wins. Try traversing a tree without recursive calls in a loop; 
you wind up modeling the stack by hand. Finally, your argument that Python was never designed this way is certainly true, 
but does little to convince me that it's a god design.

Seeing a recursion in a loop looks quite strange. It looks to me like hammering a screw or screwing a nail.
"""

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
    print( indent + "Anzahl der Pflichtpfade: " + str(nrMandatoryPaths) )

def setAppearanceForAllSheets(workbook, worksheetAutoIndexedMapping, worksheetPaths, worksheetCSVPaths):
    # Allgemein
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
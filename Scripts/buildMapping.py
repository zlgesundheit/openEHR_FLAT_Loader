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
from Scripts import pathObjectClass
from Scripts import handleConfig

import sys

# TODO check unused imports
#sys.setrecursionlimit(10000)

indent = "\t"
workdir = os.getcwd()

############################### Main ###############################

def main(manualTaskDir,templateName, csv_dataframe, pathArray, allindexesareone):
    """

    Args:
      manualTaskDir: param templateName:
      csv_dataframe: param pathArray:
      allindexesareone: 
      templateName: 
      pathArray: 

    Returns:

    """
    print("MappingListGen is running:")
    
    # Create Excel-File
    excelPath = os.path.join(manualTaskDir, templateName + '_MAPPING.xlsx')
    workbook = xlsxwriter.Workbook(excelPath)

    worksheetAutoIndexedMapping = workbook.add_worksheet('Auto-indexed Mapping')
    worksheetPaths = workbook.add_worksheet('FLAT_Paths')
    worksheetCSVPaths = workbook.add_worksheet('CSV_Items')

    # Set Appearance
    mandatory_cell_format, cond_mandatory_cell_format = set_appearances(workbook, worksheetAutoIndexedMapping, worksheetPaths, worksheetCSVPaths)

    numberOfCSVitems = len(csv_dataframe.columns)

    # Compose CSV_Items Worksheet
    compose_csv_item_worksheet(csv_dataframe, worksheetCSVPaths)
    # Compose FLAT_Path Worksheet
    compose_flatpath_worksheet(pathArray, worksheetPaths)
    # Compose Auto-indexed Mapping Worksheet
    compose_mapping_worksheet(worksheetAutoIndexedMapping, pathArray, numberOfCSVitems, allindexesareone, mandatory_cell_format, cond_mandatory_cell_format)

    workbook.close()
    print ("Generated the (empty) Mapping-Table")
    print ("\n")

############################### Methods ###############################

def compose_mapping_worksheet(worksheetMapping, pathArray, numberOfCSVitems, allindexesareone, mandatory_cell_format, cond_mandatory_cell_format):
    """Composes mapping-worksheet based on index-values from userinput.

    Args:
      worksheetMapping: param pathArray:
      numberOfCSVitems: param allindexesareone:
      mandatory_cell_format: param cond_mandatory_cell_format:
      pathArray: 
      allindexesareone: 
      cond_mandatory_cell_format: 

    Returns:

    """

    # add paths + dropdown list
    local_indexPathDict = {}
    list_of_queried_index_elements = []
    row = 1
    alreadyAddedPath = []
    for path in pathArray:
        if path.is_mandatory:
            formatting = mandatory_cell_format
        elif path.is_conditional:
            formatting = cond_mandatory_cell_format
        else:
            formatting = None

        # Falls Path keinen Index 
        if not path.hasIndex:
            # Wenn Suffix dann pro Suffix einen Pfad
            if path.hasSuffix:
                for suffix in path.suffixList:
                    add_path_with_suffix(path.pathString, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                    add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                    row += 1
            elif not path.hasSuffix:
                add_path_without_suffix(path.pathString, row, worksheetMapping, numberOfCSVitems, formatting)
                # Pflichtangabe
                add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                row += 1
        # Falls Path Index hat
        elif path.hasIndex:   # how to get the index number that shall not be quieried?
            # Abfrage von Indexen   (hier werden alle Pfade durchlaufen die mind. einen Index haben und nur einmal gefragt)
            # Wir springen hier von PfadObjekt zu Pfadobjekt. Dadurch muessen wir die erfassten Indexpfadwerte zwischenspeichern 
            # um sie den PFadobjekten hinzufuegen zu koennen, die danach kommen und fuer die kein Input kommt.
            for indexPath in path.indexPathDict:
                if not indexPath in list_of_queried_index_elements:
                    if allindexesareone == "0":
                        print ("\n")
                        print (f'Das nachfolgende Element kann in der Composition beliebig oft wiederholt werden:')
                        print (f'{indexPath}')
                        print (f'Wie oft wird das Element maximal pro Composition vorkommen?')
                        userInput = int(input('Anzahl der Messwerte: '))
                    else:
                        userInput = 1
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
                        #String_with_0_index = path.pathString.replace('<<index>>',(str(j)))
                        if path.hasSuffix:
                            for suffix in path.suffixList:
                                #addPathWithSuffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                                add_path_with_suffix(path.pathString, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                                add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                worksheetMapping.write('B'+str(row+1),str(j), formatting)
                                row += 1
                        elif not path.hasSuffix:
                            #addPathWithoutSuffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems, formatting)
                            add_path_without_suffix(path.pathString, row, worksheetMapping, numberOfCSVitems, formatting)
                            # Pflichtangabe
                            add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                            worksheetMapping.write('B'+str(row+1),str(j), formatting)
                            row += 1
            
################################################################################################################################################
###################################          Part needs to be discussed since its smelly                ########################################
################################################################################################################################################
            # Das Problem mit mehreren Indexen (n^m^k etc.) :
            # Permutationen klappen nicht, weil die Maximalwerte der einzelnen Indexstellen dann nicht Beachtung finden
            # Liste von Listen mit validen Kombinationen (n-Laufvariablen die hochzaehlen und an bestehende Listen anfügen...)
            # Array von Laufvariablen das durchlaufen wird war auch irgendwie Mist.
            # Idee: Stückweise Ersetzung im Pfad beginnend von links -> REKURSIV...natürlich
            ## SLOW AND DIRTY weil Python keine Rekursion in For-Schleifen kann.
            ## In Manual schreiben, dass wir nur Pfade mit bis zu 4 Indexen unterstützen :D :D -> Nochmal mit Jan diskutieren TODO
            
            # Naechstes Problem: Richtige Indexe zum Pfad in IndexAngabenArray in Zeile B schreiben, nicht direkt in den Pfad
            
            elif path.maxIndexNumber == 2:
                #realPathString = path.pathString
                for j in range(0,indexArray[0]):
                    #String_with_1_index_left = realPathString.replace('<<index>>',(str(j)),1)
                    for i in range(0,indexArray[1]):
                        #String_with_0_index = String_with_1_index_left.replace('<<index>>',(str(i)),1)
                        String_with_0_index = path.pathString # actually it has indexes but i dont want to change the variable names below
                        #if not String_with_0_index in alreadyAddedPath:
                        if path.hasSuffix:
                            for suffix in path.suffixList:
                                add_path_with_suffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                                add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                worksheetMapping.write('B'+str(row+1),str(j)+","+str(i), formatting)
                                row += 1
                        elif not path.hasSuffix:
                            add_path_without_suffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems, formatting)
                            add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                            worksheetMapping.write('B'+str(row+1),str(j)+","+str(i), formatting)
                            row += 1
                            #alreadyAddedPath.append(String_with_0_index)
            elif path.maxIndexNumber == 3:
                #somePathString = path.pathString
                for j in range(0,indexArray[0]):
                    #String_with_2_index_left = somePathString.replace('<<index>>',(str(j)),1)
                    for i in range(0,indexArray[1]):
                        #String_with_1_index = String_with_2_index_left.replace('<<index>>',(str(i)),1)
                        for k in range(0,indexArray[2]):
                            #String_with_0_index = String_with_1_index.replace('<<index>>',(str(k)),1)
                            String_with_0_index = path.pathString # actually it has indexes but i dont want to change the variable names below
                            #if not String_with_0_index in alreadyAddedPath:
                            if path.hasSuffix:
                                for suffix in path.suffixList:
                                    add_path_with_suffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                                    add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                    worksheetMapping.write('B'+str(row+1),str(j)+","+str(i)+","+str(k), formatting)
                                    row += 1
                            elif not path.hasSuffix:
                                add_path_without_suffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems, formatting)
                                add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                worksheetMapping.write('B'+str(row+1),str(j)+","+str(i)+","+str(k), formatting)
                                row += 1
                                #alreadyAddedPath.append(String_with_0_index)
            elif path.maxIndexNumber == 4:
                #somePathString = path.pathString
                
                for m in range(0,indexArray[0]):
                    #String_with_3_index_left = somePathString.replace('<<index>>',(str(m)),1)
                    for j in range(0,indexArray[1]):
                        #String_with_2_index_left = String_with_3_index_left.replace('<<index>>',(str(j)),1)
                        for i in range(0,indexArray[2]):
                            #String_with_1_index = String_with_2_index_left.replace('<<index>>',(str(i)),1)
                            for k in range(0,indexArray[3]):
                                #String_with_0_index = String_with_1_index.replace('<<index>>',(str(k)),1)
                                String_with_0_index = path.pathString # actually it has indexes but i dont want to change the variable names below
                                #if not String_with_0_index in alreadyAddedPath:
                                if path.hasSuffix:
                                    for suffix in path.suffixList:
                                        add_path_with_suffix(String_with_0_index, suffix, row, worksheetMapping, numberOfCSVitems, formatting)
                                        add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                        worksheetMapping.write('B'+str(row+1),str(m)+","+str(j)+","+str(i)+","+str(k), formatting)
                                        row += 1
                                elif not path.hasSuffix:
                                    add_path_without_suffix(String_with_0_index, row, worksheetMapping, numberOfCSVitems, formatting)
                                    add_mandatory_column_entry(path, row, worksheetMapping, formatting)
                                    worksheetMapping.write('B'+str(row+1),str(m)+","+str(j)+","+str(i)+","+str(k), formatting)
                                    row += 1
                                    #alreadyAddedPath.append(String_with_0_index)
################################################################################################################################################
    # Write Legende
    row += 1
    worksheetMapping.write('C'+str(row+1), "Legend:")
    worksheetMapping.write('C'+str(row+2), "Mandatory Path that needs to be present to get a valid Composition" , mandatory_cell_format)
    worksheetMapping.write('C'+str(row+3), "Conditionally mandatory Path that needs to be present if the 'parent'-Element is exists" , cond_mandatory_cell_format)
    worksheetMapping.write('C'+str(row+4), "Non-mandatory Path that does not need to be present to store the Composition" )
    
    # End of Auto-indexed-Mapping Sheet

def add_path_with_suffix(pathString, suffix, row, worksheetMapping, numberOfCSVitems, formatting):
    """

    Args:
      pathString: param suffix:
      row: param worksheetMapping:
      numberOfCSVitems: param formatting:
      suffix: 
      worksheetMapping: 
      formatting: 

    Returns:

    """
    worksheetMapping.write('C'+str(row+1),pathString + "|" + suffix, formatting)
    worksheetMapping.data_validation('D'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})

def add_path_without_suffix(pathString, row, worksheetMapping, numberOfCSVitems, formatting):
    """

    Args:
      pathString: param row:
      worksheetMapping: param numberOfCSVitems:
      formatting: 
      row: 
      numberOfCSVitems: 

    Returns:

    """
    worksheetMapping.write('C'+str(row+1),pathString, formatting)
    worksheetMapping.data_validation('D'+str(row+1), {'validate': 'list','source': '=CSV_Items!$A$2:$A$' + str(numberOfCSVitems +1)})

def add_mandatory_column_entry(path, row, worksheetMapping, formatting):
    """

    Args:
      path: param row:
      worksheetMapping: param formatting:
      row: 
      formatting: 

    Returns:

    """
    # Pflichtangabe
    if path.is_mandatory:
        worksheetMapping.write('A'+str(row+1)," P ", formatting)
    # Bedingt Pflichtelement
    if path.is_conditional:
        worksheetMapping.write('A'+str(row+1),"bP", formatting)

def set_next_index(realPathString, resultArray, indexArray, i):
    """

    Args:
      realPathString: param resultArray:
      indexArray: param i:
      resultArray: 
      i: 

    Returns:

    """
    if not "<<index>>" in realPathString:
        return realPathString
    for j in range(0, indexArray[i]):
        nuuuuPath = realPathString.replace('<<index>>',(str(j)),1)
        print(nuuuuPath)
        nuuuuPath = set_next_index(nuuuuPath, resultArray, indexArray, i + 1)

def compose_csv_item_worksheet(df, worksheetCSVPaths):
    """Worksheet mit Infos zu den Daten / CSV

    Args:
      df: param worksheetCSVPaths:
      worksheetCSVPaths: 

    Returns:

    """
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

def compose_flatpath_worksheet(pathArray, worksheetPaths):
    """Worksheet mit Infos zu den FLAT-Pfaden

    Args:
      pathArray: param worksheetPaths:
      worksheetPaths: 

    Returns:

    """
    j = 1
    nrMandatoryPaths = 0
    for path in pathArray:
        worksheetPaths.write(j, 0, path.pathString)
        worksheetPaths.write(j, 1, path.rmType)
        if path.is_mandatory:
            worksheetPaths.write(j, 2, "Pflichtpfad")
            nrMandatoryPaths += 1
        # Bedingt Pflichtelement
        if path.is_conditional:
            worksheetPaths.write('C'+str(j),"bedingt Pflicht")
        j += 1
    print( indent + "Anzahl der Pflichtpfade (ohne Suffixe): " + str(nrMandatoryPaths) )

def set_appearances(workbook, worksheetAutoIndexedMapping, worksheetPaths, worksheetCSVPaths):
    """

    Args:
      workbook: param worksheetAutoIndexedMapping:
      worksheetPaths: param worksheetCSVPaths:
      worksheetAutoIndexedMapping: 
      worksheetCSVPaths: 

    Returns:

    """
    # Allgemein
    # https://xlsxwriter.readthedocs.io/format.html#set_align

    # Mandatory-Items
    mandatory_cell_format = workbook.add_format()
    mandatory_cell_format.set_bg_color('#FF0000') # red
    #mandatory_cell_format.set_align('center') # left center right fill justify center_across distributed

    cond_mandatory_cell_format = workbook.add_format()
    cond_mandatory_cell_format.set_bg_color('#FF6600') # orange
    #cond_mandatory_cell_format.set_align('center') # left center right fill justify center_across distributed

    # Header
    header_cell_format = workbook.add_format()
    header_cell_format.set_bg_color('#808080') # gray
    header_cell_format.set_align('center') # left center right fill justify center_across distributed
    #header_cell_format.set_align('valign')

    # Flat-Pfad Worksheet
    worksheetPaths.set_column('A:A', 100)
    worksheetPaths.set_column('B:B', 60)
    worksheetPaths.set_column('C:C', 40)
    worksheetPaths.write('A1', 'FLAT-Path', header_cell_format)
    worksheetPaths.write('B1', 'rmType', header_cell_format)
    worksheetPaths.write('C1', 'Mandatory Paths', header_cell_format)

    # CSV-Items
    worksheetCSVPaths.set_column('A:A', 100)
    worksheetCSVPaths.set_column('B:B', 60)
    worksheetCSVPaths.write('A1', 'CSV-Column', header_cell_format)
    worksheetCSVPaths.write('B1', 'Example-Value', header_cell_format)

    # Mapping
    worksheetAutoIndexedMapping.write('A1', '', header_cell_format) 
    worksheetAutoIndexedMapping.write('B1', 'Index(e)', header_cell_format)
    worksheetAutoIndexedMapping.write('C1', 'FLAT-Path (Data field in later composition - if mapped)', header_cell_format)
    worksheetAutoIndexedMapping.write('D1', 'Map CSV-Column to Path (Dropdown-Selector)', header_cell_format) 
    worksheetAutoIndexedMapping.write('E1', 'Set Metadata directly (optional)', header_cell_format) 
    worksheetAutoIndexedMapping.set_column('A:A', 5)
    worksheetAutoIndexedMapping.set_column('B:B', 15)
    worksheetAutoIndexedMapping.set_column('C:C', 100)
    worksheetAutoIndexedMapping.set_column('D:D', 50)
    worksheetAutoIndexedMapping.set_column('E:E', 35)

    return mandatory_cell_format, cond_mandatory_cell_format

if __name__ == '__main__':
    main()
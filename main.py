#########################################################################
# ETL-Pipeline from CSV to openEHR-Compositions
# 
# 1. Upload Template and get WebTemplate
# 2. Generate Mapping List from WebTemplate
# 3. (Manual Task) Mapping-List ausfüllen
# 4. Build Compositions
#
# Developed and tested with Python 3.8.10
#
# Jendrik Richter (UMG)
#########################################################################
# Standard library imports
import os.path
from os import getcwd
# Third party imports
import pandas as pd
# Local application/script imports
from Scripts import configHandler
from Scripts import handleOPT
from Scripts import buildComp
from Scripts import pathExport
from Scripts import mappingListGen
from Scripts import ucc_uploader

#Init Config-Object
config = configHandler.config()
indent = "\t"
workdir = getcwd()

############################### Main ###############################
def main():
    
    # Check if all directories exist otherwise create them
    checkIfDirsExists()

    # Show Explanatory Text on how to use the tool and what steps to perform to the User
    printInfoText()

    # Query User Input
    choosenStep = input("Bitte Ziffer eingeben: ")

    # Run Script Part/Step that was choosen by the user
    runStep(choosenStep)

    # Terminate

############################### Methods ###############################
def runStep(choosenStep):
    if (choosenStep == str(1)):
        # Upload OPT to openEHR-Repo if necessary
        webTemp = handleOPT.main(config)
        
        # Extrahiere Pfade in Dict 
        pathArray = pathExport.main(webTemp, config.templateName)

        # Baue Mapping
        mappingListGen.main(config.templateName, config.inputCSV, pathArray)

    elif(choosenStep == str(2)):
        resArray = buildComp.main(config)

        #Create EHRs for all patients in csv
        if config.createehrs == "1":
            csvPath = os.path.join(workdir, "Input", "CSV", config.inputCSV + ".csv")
            csv_dataframe = pd.read_csv(csvPath, header=0, delimiter=";", dtype=str)
            anzahl_eintraege = len(csv_dataframe.index)

            print (f'Create {anzahl_eintraege} EHRs:')
            csv_dataframe = ucc_uploader.createEHRsForAllPatients(config.targetAdress, config.targetAuthHeader, csv_dataframe, config.subjectidcolumn , config.subjectnamespacecolumn)
            csv_dataframe.to_csv(csvPath, sep=";", index = False, encoding = "UTF-8")
        else:
            print ("EHR Creation is disabled in Config.ini")
            pass

        # Send resource to server
        if config.directupload == "1":
            csvPath = os.path.join(workdir, "Input", "CSV", config.inputCSV + ".csv")
            csv_dataframe = pd.read_csv(csvPath, header=0, delimiter=";", dtype=str)
            anzahl_eintraege = len(csv_dataframe.index)

            print ("Upload Compositions:")
            quick_and_dirty_index = 0
            for res in resArray:
                ucc_uploader.uploadResourceToEhrIdFromCSV(config.targetAdress, config.targetAuthHeader, csv_dataframe, res, config.templateName, quick_and_dirty_index)

                quick_and_dirty_index += 1
        else:
            print ("Direct Upload is disabled in Config.ini")
            pass

def printInfoText():
    print(os.linesep)
    print("Willkommen im openEHR_FLAT_Loader-Commandline-Tool")
    print(os.linesep)
    print("Mithilfe dieses Tools können beliebige tabellarische Daten in das interoperable openEHR-Format transformiert werden."
        + os.linesep
        + os.linesep + "Geben Sie in der Config-Datei entsprechend die Variablen für Template, CSV und Repository an. Führen Sie Schritt 1"
        + os.linesep + "aus, um erst ein Mapping zu erzeugen, dass (nach manuellem Ausfüllen) in Schritt 2 für die automatisierte"
        + os.linesep + "Erzeugung von openEHR-Ressourcen aus ihren tabellarischen Daten genutzt wird."
        + os.linesep
        # Auswahl von im OPT-Ordner existierenden Dateien + Abfrage welche genutzt werden soll? TODO
        # TODO Columns wie Namespace SubjectId etc von Hand aus CSV auswählbar machen -> ohne in die Config gehen zu müssen
        + os.linesep + indent +"Schritt 1: OPT hochladen und Mapping erzeugen" 
        + os.linesep + indent +"Schritt 2: Ressourcen erzeugen"
        + os.linesep + "Für das Anlegen von EHRs und den Upload setzen Sie in der Config entsprechend 'createehrs' und 'directupload' auf den Wert 1"
    )
    print(os.linesep + "Auswahl:")
    print(os.linesep)

def createDir(path):
    access_rights = 0o755
    try:
        os.mkdir(path, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)

def checkIfDirsExists():
    workdir  = os.getcwd()
    manualTasksDir = os.path.join(workdir, "ManualTasks")
    outputDir = os.path.join(workdir, "Output")

    if not os.path.isdir(manualTasksDir):
        createDir(manualTasksDir)

    if not os.path.isdir(outputDir):
        createDir(outputDir)

if __name__ == '__main__':
    main()
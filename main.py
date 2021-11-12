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
from Scripts import buildExampleComp

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
    choosenStep = input("Bitte Schritt wählen (1,2,3) eingeben: ")

    # Run Script Part/Step that was choosen by the user
    runStep(choosenStep)

    # Terminate

############################### Methods ###############################
def runStep(choosenStep):
    if (choosenStep == str(1)):
        # Upload OPT to openEHR-Repo if necessary
        webTemp = handleOPT.main(config)
        
        # Extrahiere Pfade in Array von Pfadobjekten 
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
                #Wird dann in buildComp auffgerufen, liest hier die aktuelle CSV mit ehrIds ein
                ehrId = csv_dataframe['ehrId'][quick_and_dirty_index]
                ucc_uploader.uploadResourceToEhrId(config.targetAdress, config.targetAuthHeader, ehrId, res, config.templateName)

                quick_and_dirty_index += 1
        else:
            print ("Direct Upload is disabled in Config.ini")
            pass
    
    elif(choosenStep == str(3)):
        # Upload OPT to openEHR-Repo if necessary
        webTemp = handleOPT.main(config)
        
        # Extrahiere Pfade in Array von Pfadobjekten 
        pathArray = pathExport.main(webTemp, config.templateName)

        # Build Minimal Example
        buildExampleComp.main(workdir, pathArray, config.templateName, config.targetAdress, config.targetAuthHeader, "min")
        # Build Maximal Example
        buildExampleComp.main(workdir, pathArray, config.templateName, config.targetAdress, config.targetAuthHeader, "max")

def printInfoText():
    print(os.linesep)
    print("Willkommen im openEHR_FLAT_Loader-Commandline-Tool")
    print(os.linesep)
    print("Mithilfe dieses Tools können beliebige tabellarische Daten in das interoperable openEHR-Format transformiert werden."
        + os.linesep + "Geben Sie in der Config-Datei entsprechend die Variablen für Template, CSV und Repository an."
        + os.linesep
        # Auswahl von im OPT-Ordner existierenden Dateien + Abfrage welche genutzt werden soll? TODO
        # TODO Columns wie Namespace SubjectId etc von Hand aus CSV auswählbar machen -> ohne in die Config gehen zu müssen
        + os.linesep + indent +"Schritt 1: OPT hochladen und Mapping erzeugen" 
        + os.linesep + indent +"Schritt 2: Ressourcen erzeugen (und hochladen)"
        + os.linesep + indent + indent + "EHRs erzeugen mit 'createehrs   = 1' in config.ini"
        + os.linesep + indent + indent + "Upload        mit 'directupload = 1' in config.ini"
        + os.linesep + indent +"Schritt 3: Erzeuge Min/Max FLAT/CANONICAL Example-Composition -- WORK IN PROGRESS --"
    )
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
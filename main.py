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
import sys
import traceback
# Third party imports
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
    global guessed_encoding

    # Check if all directories exist otherwise create them
    checkIfDirsExists()

    # Show Explanatory Text on how to use the tool and what steps to perform to the User
    printInfoText()

    # Query User Input
    print ("    Please enter number 1,2 or 3 to run the desired step: ")
    print ("\n")
    choosenStep = input("\t") 
    # WE could add a nice selector menue with 'whaaaaat' or 'inquirer' but that would mean the user needs to install an additional package: no
    # Input zeigt nichts mehr an, weil durch @echo off im .bat die Ausgabe cleaner wird...

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

        csv_dataframe = configHandler.readCSVasDataFrame(config.inputCSV)

        # Baue Mapping
        mappingListGen.main(config.templateName, csv_dataframe, pathArray, allindexesareone = config.allindexesareone)

    elif(choosenStep == str(2)):
        resArray = buildComp.main(config)

        #Create EHRs for all patients in csv
        if config.createehrs == "1":
            csv_dataframe = csv_dataframe = configHandler.readCSVasDataFrame(config.inputCSV)
            anzahl_eintraege = len(csv_dataframe.index)

            print (f'Create {anzahl_eintraege} EHRs:')
            csv_dataframe = ucc_uploader.createEHRsForAllPatients(config.targetAdress, config.targetAuthHeader, csv_dataframe, config.subjectidcolumn , config.subjectnamespacecolumn)
            csvPath = os.path.join(workdir, 'Input', 'CSV', config.inputCSV + '.csv')
            csv_dataframe.to_csv(csvPath, sep=";", index = False, encoding = "UTF-8")
        else:
            print ("EHR Creation is disabled in Config.ini")
            pass

        # Send resource to server
        if config.directupload == "1":
            csv_dataframe = configHandler.readCSVasDataFrame(config.inputCSV)
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
    print("    Welcome to the openEHR_FLAT_Loader-Commandline-Tool!")
    print(os.linesep)
    print("    This tool allows you to transform tabular data into the interoperable openEHR format."
        + os.linesep + "                                                             (given an existing template)"
        + os.linesep 
        + os.linesep + "    Please set variables for template, data/csv-file and repository in config.ini."
        + os.linesep
        # Auswahl von im OPT-Ordner existierenden Dateien + Abfrage welche genutzt werden soll? TODO
        # TODO Columns wie Namespace SubjectId etc von Hand aus CSV auswählbar machen -> ohne in die Config gehen zu müssen
        + os.linesep + indent + "Schritt 1: OPT hochladen und Mapping erzeugen" 
        + os.linesep + indent + indent +  "   Indexe  mit 'allindexesareone  = 1' in config.ini automatisch auf 1 setzen"
        + os.linesep
        + os.linesep + indent + "Schritt 2: Ressourcen erzeugen (und hochladen)"
        + os.linesep + indent + indent +  "   EHRs    mit 'createehrs   = 1' in config.ini erzeugen"
        + os.linesep + indent + indent +  "   Upload  mit 'directupload = 1' in config.ini ausführen"
        + os.linesep
        + os.linesep + indent + "Schritt 3: Erzeuge Min/Max FLAT/CANONICAL Example-Composition"
        + os.linesep + indent + indent +  "   -- WORK IN PROGRESS --"
    )
    print(os.linesep)

def createDir(path):
    access_rights = 0o755
    try:
        os.mkdir(path, access_rights)
    except OSError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
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
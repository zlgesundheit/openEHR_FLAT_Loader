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
from pathlib import Path
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
        print("The OPT-File is uploaded to the openEHR-Repo") # TODO this print should be done by the other scripts after they performed, not in the runMain, also see others below
        
        # Extrahiere Pfade in Dict 
        pathsDict = pathExport.main(webTemp, config.templateName)
        print("Extracted FLAT-Paths from the WebTemplate")

        # Baue Mapping
        mappingListGen.main(config.templateName, config.inputCSV, pathsDict)
        print("Generated the (empty) Mapping-Table")

    elif(choosenStep == str(2)):
        resArray = buildComp.main(config)

        # Create EHRs
        patient_id_column_name = "sha1"
        subject_namespace_column_name = "upload_subject_namespace"
        csvPath = Path("C:\\Users\\richter122\\Desktop\\UCC_EHRBase\\FLAT_Loader_UCC\\Input\\CSV\\ucc_score_gesamtdaten_erweitert_utf8.csv")
        csv_dataframe = pd.read_csv(csvPath, header=0, delimiter=";", dtype=str)
        anzahl_eintraege = len(csv_dataframe.index)

        ## TODO Server und Auth sind in UCC Uploader hardkodiert!

        #Create EHRs for all patients in csv
        if config.createehrs == "1":
            print (f'Create {anzahl_eintraege} EHRs')
            csv_dataframe = ucc_uploader.createEHRsForAllPatients(csv_dataframe, patient_id_column_name, subject_namespace_column_name)
            csv_dataframe.to_csv(csvPath, sep=";", index = False, encoding = "UTF-8")
        else:
            print ("EHR Creation is disabled in Config.ini")
            pass

        # Send resource to server
        if config.directupload == "1":
            print ("Upload Compositions")
            quick_and_dirty_index = 0
            for res in resArray:
                ucc_uploader.uploadResourceToEhrIdFromCSV(config.targetAdress , csv_dataframe, res, config.templateName, quick_and_dirty_index)

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
        + os.linesep + "und Schritt 2 aus, um erst ein Mapping zu erzeugen, dass (nach manuellem Ausfüllen) für die automatisierte"
        + os.linesep + "Erzeugung von openEHR-Ressourcen aus ihren tabellarischen Daten genutzt wird."
        + os.linesep
        # Auswahl von im OPT-Ordner existierenden Dateien + Abfrage welche genutzt werden soll
        + os.linesep + indent +"Schritt 1: OPT hochladen und Mapping erzeugen" 
        + os.linesep + indent +"Schritt 2: Ressourcen erzeugen"
    )
    print(os.linesep + "Auswahl:"
        + os.linesep + indent +"'1': OPT-laden und Mapping-Liste für manuelle Ausfüllen erzeugen."
        + os.linesep + indent +"'2': Auf Basis des ausgefüllten Mappings und der Quelldaten-CSV die Ressourcen (Compositions) erzeugen"
        + os.linesep + indent +"     Config 'create_ehrs'   auf 1 setzen um EHRs auf dem Server zu erzeugen   (Schreibt ehrIds in CSV-Spalte: ehrId)"
        + os.linesep + indent +"     Config 'direct_upload' auf 1 setzen um Compositions zum Server zu schicken (Nutzt ehrIds aus CSV-Spalte: ehrId)"
        + os.linesep + indent +"'coming later': Upload Resources to Server."
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
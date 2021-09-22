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
# Third party imports
# Local application/script imports
from Scripts import configHandler
from Scripts import handleOPT
from Scripts import buildComp
from Scripts import pathExport
from Scripts import mappingListGen

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
        buildComp.main()

    elif(choosenStep == str(3)):
        configHandler.queryConfEntry()
        #config = configHandler.readConf()

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
        + os.linesep + indent +"'2': Auf Basis des ausgefüllten Mappings und der Quelldaten-CSV die Ressourcen erzeugen."
        + os.linesep + indent +"'3': Werte für Konfig-Datei eigeben."
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
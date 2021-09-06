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

############################### Main ###############################
def main():
    #Read Config
    config = configHandler.readConf()
    
    # Check if all directories exist otherwise create them
    checkIfDirsExists()

    # Check if config exists otherwise request input from user
    checkIfConfExists()

    # Show Explanatory Text to the User
    printInfoText()

    # Query User Input
    choosenStep = input("Auswahl: ")

    # Run Script Part/Step that was choosen by the user
    runStep(choosenStep)

    # Terminate

############################### Methods ###############################
def runStep(choosenStep):

    if (choosenStep == str(1)):
        handleOPT.main()

    elif(choosenStep == str(2)):
        buildComp.main()

    elif(choosenStep == str(3)):
        configHandler.queryConfEntry()
        config = configHandler.readConf()

def printInfoText():
    print("Mithilfe dieses Tools kann ein OPT hochgeladen und eine Mapping Liste, welche manuell auszufüllen ist, erzeugt werden." 
        + os.linesep + "Schritt 1: OPT hochladen und Mapping erzeugen" 
        + os.linesep + "Schritt 2: Ressourcen erzeugen")

    print(os.linesep + "Optionen:")
    print("Option 1: OPT-laden und Mapping-Liste für manuelle Ausfüllen erzeugen.")
    print("Option 2: Auf Basis des ausgefüllten Mappings und der Quelldaten-CSV die Ressourcen erzeugen.")
    print("Option 3: Werte für Konfig-Datei eigeben.")
    print("")

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
    intermFilesDir = os.path.join(workdir, "IntermFiles")
    manualTasksDir = os.path.join(workdir, "ManualTasks")
    outputDir = os.path.join(workdir, "Output")

    if not os.path.isdir(intermFilesDir):
        createDir(intermFilesDir)

    if not os.path.isdir(manualTasksDir):
        createDir(manualTasksDir)

    if not os.path.isdir(outputDir):
        createDir(outputDir)

def checkIfConfExists():
    confFile_path = 'config.ini'
    if os.path.isfile(confFile_path):
        # Load existing Config
        config = configHandler.readConf()
        print("Loaded existing Config." + os.linesep)
    else:
        # Query Input from User
        configHandler.queryConfEntry()

if __name__ == '__main__':
    main()
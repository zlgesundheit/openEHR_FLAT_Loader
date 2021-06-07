#############################################################################
# ETL-Pipeline from CSV to openEHR-Compositions
# 
# 1. Upload Template and get WebTemplate
# 2. Generate Mapping List from WebTemplate
# 3. (Manual Task) Mapping-List ausfüllen
# 4. Build Compositions
# Developed and tested with Python 3.8.3
#
# Jendrik Richter (UMG)
##############################################################################
# Standard library imports
import os.path
# Third party imports
import configparser
# Local application imports
from Scripts import configHandler
from Scripts import handleOPT as opt
from Scripts import buildComp as bob

# See if config already exists
confFile_path = 'config.ini'
if os.path.isfile(confFile_path):
    # Load existing Config
    config = configHandler.readConf()
    print("Loaded existing Config." + os.linesep)
else:
    # Open Config-Entry Dialogue
    configHandler.queryConfEntry()
    config = configHandler.readConf()

print("Mithilfe dieses Tools kann ein OPT hochgeladen und eine Mapping Liste, welche manuell auszufüllen ist, erzeugt werden." + os.linesep + "Schritt 1: OPT hochladen und Mapping erzeugen" + os.linesep + "Schritt 2: Ressourcen erzeugen")

print(os.linesep + "Optionen:")
print("Option 1: OPT-laden und Mapping-Liste für manuelle Ausfüllen erzeugen.")
print("Option 2: Auf Basis des ausgefüllten Mappings und der Quelldaten-CSV die Ressourcen erzeugen.")
print("Option 3: Werte für Konfig-Datei eigeben.")
print("")
chooseStep = input("Auswahl:"+ os.linesep)
if (chooseStep == str(1)):
    opt.handleOPT(
        config['targetRepo']['workdir'], 
        config['targetRepo']['templateName'], 
        config['targetRepo']['inputCSV'], 
        config['targetRepo']['targetRepoAdress'],
        config['targetRepo']['targetRepoUser'],
        config['targetRepo']['targetRepoPw'],
        config['targetRepo']['targetflatAPIadress'],
        config['targetRepo']['targetopenEHRAPIadress']
        )
elif(chooseStep == str(2)):
    bob.buildComp(
        config['targetRepo']['workdir'], 
        config['targetRepo']['templateName'],
        config['targetRepo']['inputCSV']
        )
elif(chooseStep == str(3)):
    configHandler.queryConfEntry()
    config = configHandler.readConf()
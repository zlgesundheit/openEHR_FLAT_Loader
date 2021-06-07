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
  print("Loaded existing Config.")
else:
  print("Waiting for User-Input...")
  defaultInp = input("Möchten Sie die Default-Config verwenden? (y/n): " )
  if (defaultInp == "y"):
    # Store and Load Default-Conf
    targetRepoAdress = input("Geben sie die Base-Adress des Target-Repos an (e.g. http://141.5.100.199/ehrbase): ")
    configHandler.setTargetRepoAdress(targetRepoAdress)
    configHandler.storeConf()
    config = configHandler.readConf()
  else:
    # User-Input for new Config
    configHandler.queryConfEntry()
    config = configHandler.readConf()

print(os.linesep + "Auswahl:")
print("Schritt 1: OPT-laden und Mapping-Liste für manuelle Ausfüllen erzeugen.")
print("Schritt 2: Auf Basis des ausgefüllten Mappings und der Quelldaten-CSV die Ressourcen erzeugen.")
print("")
chooseStep = input("Welcher Prozessschritt soll ausgeführt werden?"+ os.linesep +"(1=Mapping-Liste erzeugen,2=Compositions bauen): ")
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
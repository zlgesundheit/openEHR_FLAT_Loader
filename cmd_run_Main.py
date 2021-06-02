#############################################################################
# (Manual) ETL-Pipeline from CSV to openEHR-Compositions
# 
# 1. Upload Template and get FLAT-Example-Composition and WebTemplate (1_HandleOPT.py)
# 2. (Manual Task) Adapt FLAT-Composition to include all needed Template-Fields  <-- This will be automated in the near future
# 3. Generate Mapping List
# 4. (Manual Task) Mapping-List ausfüllen
# 5. Build Compositions
# Developed and tested with Python 3.8.3
#
# Jendrik Richter (UMG)
#
# TODO List:
# 1. Auslesen der Pfade aus dem WebTemplate statt aus der Example Comp (in HandleOPT)
##############################################################################
import configparser
import os.path
import configHandler

# See if config already exists
confFile_path = '.config.ini'
if os.path.isfile(confFile_path):
  # Load existing Config
  config = configHandler.readConf()
  print("Loaded existing Config.")
else:
  print("Waiting for User-Input...")
  defaultInp = input("Möchten Sie die Default-Config verwenden? (y/n): " )
  if (defaultInp == "y"):
    # Store and Load Default-Conf
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
  import HandleOPT as opt
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
  import BuildComp as bob
  bob.buildComp(
    config['targetRepo']['workdir'], 
    config['targetRepo']['templateName'],
    config['targetRepo']['inputCSV']
    )
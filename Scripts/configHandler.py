# Load and Store Config
#
# Jendrik Richter (UMG)
####################################
# Standard library imports
# Third party imports
import configparser
# Local application imports
from Scripts import handleOPT

configParser = configparser.ConfigParser()

def readConf():
    configParser.read('config.ini')
    return configParser

def storeDefaultConf():
    # otherwise create new conf-file and set defaults
    configParser['DEFAULT'] = {
        'templateName': 'ZLG_Testdaten',
        'inputCSV':'test1'
        }
    configParser['targetRepo'] = {
        'targetRepoAdress':'http://141.5.100.115/ehrbase',
        'targetAuthHeader':'Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=',
        'targetflatAPIadress':'/rest/ecis/v1/',
        'targetopenEHRAPIadress':'/rest/openehr/v1/'
    }
    with open('config.ini', 'w') as configfile:
        configParser.write(configfile)

def setLocalEnv(templateName, inputCSV):
    config = readConf()
    config['DEFAULT'] = {
    'templateName': templateName,
    'inputCSV':inputCSV
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def setTargetRepo(targetRepoAdress, targetflatAPIadress, targetopenEHRAPIadress):
    config = readConf()
    config['targetRepo'] = {
        'targetRepoAdress':targetRepoAdress,
        'targetflatAPIadress':targetflatAPIadress,
        'targetopenEHRAPIadress':targetopenEHRAPIadress
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def queryConfEntry():
    if input("Default-Conf benutzen? (y/n): ") == "y":
        storeDefaultConf()
        return configParser
    else:
        #Request input for new Conf
        templateName = input("Name des Templates: ")
        inputCSV = input("Name der CSV: ")
        setLocalEnv(templateName, inputCSV)

        targetRepoAdress = input("Repo-Adresse (Bsp.: https://IP/ehrbase): ")
        targetRepoUser = input("Nutzername: ")
        targetRepoPw = input("Passwort: ")
        targetAuthHeader = handleOPT.getAuthHeader(targetRepoUser, targetRepoPw)

        targetflatAPIadress = input("FLAT-Endpunkt (Bsp.: /rest/ecis/v1/): ")
        targetopenEHRAPIadress = input("openEHR-API (Bsp.: /rest/openehr/v1/): ")
        setTargetRepo(targetRepoAdress, targetAuthHeader, targetflatAPIadress, targetopenEHRAPIadress)

        configParser.read('config.ini')

        return configParser
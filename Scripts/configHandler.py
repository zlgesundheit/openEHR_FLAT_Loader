# Load and Store Config
#
# Jendrik Richter (UMG)
####################################
# Standard library imports
# Third party imports
import configparser
# Local application imports
from Scripts import handleOPT

config = configparser.ConfigParser()

def readConf():
    config.read('config.ini')
    return config

def storeDefaultConf():
    # otherwise create new conf-file and set defaults
    config['DEFAULT'] = {
        'workdir': 'C:\\Users\\richter122\\git-projects\\openehr_flat_loader',
        'templateName': 'ZLG_Testdaten',
        'inputCSV':'test1'
        }
    config['targetRepo'] = {
        'targetRepoAdress':'http://141.5.100.115/ehrbase',
        'targetAuthHeader':'Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=',
        'targetflatAPIadress':'/rest/ecis/v1/',
        'targetopenEHRAPIadress':'/rest/openehr/v1/'
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def setLocalEnv(workdir, templateName, inputCSV):
    config['DEFAULT'] = {
    'workdir': workdir,
    'templateName': templateName,
    'inputCSV':inputCSV
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def setLoginData(authHeader):
    config['targetRepo'] = {
        'targetAuthHeader':authHeader
    }

def setTargetRepoAdress(targetRepoAdress):
    config['targetRepo'] = {
        'targetRepoAdress':targetRepoAdress,
    }

def setTargetRepo(targetRepoAdress, targetAuthHeader, targetflatAPIadress, targetopenEHRAPIadress):
    config['targetRepo'] = {
        'targetRepoAdress':targetRepoAdress,
        'targetAuthHeader':targetAuthHeader,
        'targetflatAPIadress':targetflatAPIadress,
        'targetopenEHRAPIadress':targetopenEHRAPIadress
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def queryConfEntry():
    #Query entrys for new Conf
    workdir = input("Pfad zum Work-Dir: ")
    templateName = input("Name des Templates: ")
    inputCSV = input("Name der CSV: ")
    setLocalEnv(workdir, templateName, inputCSV)
    targetRepoAdress = input("Repo-Adresse (Bsp.: https://IP/ehrbase): ")
    targetRepoUser = input("Nutzername: ")
    targetRepoPw = input("Passwort: ")
    targetAuthHeader = handleOPT.getAuthHeader(targetRepoUser, targetRepoPw)
    targetflatAPIadress = input("FLAT-Endpunkt (Bsp.: /rest/ecis/v1/): ")
    targetopenEHRAPIadress = input("openEHR-API (Bsp.: /rest/openehr/v1/): ")
    setTargetRepo(targetRepoAdress, targetAuthHeader, targetflatAPIadress, targetopenEHRAPIadress)
    config.read('config.ini')
    return config
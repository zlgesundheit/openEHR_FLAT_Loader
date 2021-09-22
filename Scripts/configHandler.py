# Load and Store Config
#
# Jendrik Richter (UMG)
####################################
# Standard library imports
import base64
import configparser
# Third party imports
# Local application imports

configParser = configparser.ConfigParser()

class config():
    targetAdress = 'http://141.5.100.115/ehrbase'
    targetAuthHeader = 'Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ='  
    targetopenEHRAPIadress = '/rest/openehr/v1/'
    targetflatAPIadress = '/rest/ecis/v1/'
    templateName = 'ZLG_Testdaten'
    inputCSV = 'test1'

    def __init__(self):
        # TODO Exception Handling if config not exist etc.? -> maybe query conf if non exists -> see def queryConfEntry(self): below
        configParser.read('config.ini')
        self.targetAdress            = configParser['targetRepo']['targetRepoAdress']
        self.targetAuthHeader        = configParser['targetRepo']['targetAuthHeader']
        self.targetopenEHRAPIadress  = configParser['targetRepo']['targetopenEHRAPIadress']
        self.targetflatAPIadress     = configParser['targetRepo']['targetflatapiadress']
        self.templateName            = configParser['DEFAULT']['templateName']
        self.inputCSV                = configParser['DEFAULT']['inputCSV']

    def loadNamesForOPTandCSV(self):
        return self.templateName, self.inputCSV

    def setFilenames(templateName, inputCSV):
        configParser.read('config.ini')
        configParser['DEFAULT'] = {
            'templateName': templateName,
            'inputCSV':inputCSV
        }
        with open('config.ini', 'w') as configfile:
            configParser.write(configfile)

    def setTargetRepo(targetRepoAdress, targetflatAPIadress, targetopenEHRAPIadress):
        configParser.read('config.ini')
        configParser['targetRepo'] = {
            'targetRepoAdress':targetRepoAdress,
            'targetflatAPIadress':targetflatAPIadress,
            'targetopenEHRAPIadress':targetopenEHRAPIadress
        }
        with open('config.ini', 'w') as configfile:
            configParser.write(configfile)

    def queryConfEntry(self):
        #Request input for new Conf
        templateName = input("Name des Templates: ")
        inputCSV = input("Name der CSV: ")
        self.setFilenames(templateName, inputCSV)

        targetRepoAdress = input("Repo-Adresse (Bsp.: https://IP/ehrbase): ")
        targetRepoUser = input("Nutzername: ")
        targetRepoPw = input("Passwort: ")
        targetAuthHeader = getAuthHeader(targetRepoUser, targetRepoPw)

        targetflatAPIadress = input("FLAT-Endpunkt (Bsp.: /rest/ecis/v1/): ")
        targetopenEHRAPIadress = input("openEHR-API (Bsp.: /rest/openehr/v1/): ")
        self.setTargetRepo(targetRepoAdress, targetAuthHeader, targetflatAPIadress, targetopenEHRAPIadress)

        configParser.read('config.ini')

        return configParser

# Get AuthHeaders
def getAuthHeader(username, pw) -> str:
    """Return the base64 encoded auth header for a given username and passwort."""
    authHeader = "Basic " + base64.b64encode((username+":"+pw).encode('ascii')).decode()
    return authHeader
# Load and Store Config
#
# Jendrik Richter (UMG)
####################################
# Standard library imports
import base64
import configparser
# Third party imports
# Local application imports

parser = configparser.ConfigParser()

class config():
    targetAdress = 'http://141.5.100.115/ehrbase'
    targetAuthHeader = 'Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ='  
    targetopenEHRAPIadress = '/rest/openehr/v1/'
    targetflatAPIadress = '/rest/ecis/v1/'
    templateName = 'ZLG_Testdaten'
    inputCSV = 'test1'
    createehrs = '1'
    directupload = '0'
    subjectidcolumn  = None
    subjectnamespace  = None

    def __init__(self):
        # TODO Exception Handling if config not exist etc.?
        parser.read('config.ini')
        self.targetAdress            = parser['targetRepo']['targetRepoAdress']
        self.targetAuthHeader        = parser['targetRepo']['targetAuthHeader']
        self.targetopenEHRAPIadress  = parser['targetRepo']['targetopenEHRAPIadress']
        self.targetflatAPIadress     = parser['targetRepo']['targetflatapiadress']
        self.templateName            = parser['DEFAULT']['templateName']
        self.inputCSV                = parser['DEFAULT']['inputCSV']
        self.createehrs              = parser['DEFAULT']['createehrs']
        self.directupload            = parser['DEFAULT']['directupload']
        self.subjectidcolumn         = parser['DEFAULT']['subjectidcolumn']
        self.subjectnamespace        = parser['DEFAULT']['subjectnamespace']

# Get AuthHeaders
def getAuthHeader(username, pw) -> str:
    """Return the base64 encoded auth header for a given username and passwort."""
    authHeader = "Basic " + base64.b64encode((username+":"+pw).encode('ascii')).decode()
    return authHeader
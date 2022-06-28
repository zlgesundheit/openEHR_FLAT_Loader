# Load and Store Config
#
# Jendrik Richter (UMG)
####################################
# Standard library imports
import base64
import configparser
import os.path
from os import getcwd
import sys
import traceback
# Third party imports
import pandas as pd
from chardet import detect
# Local application imports

parser = configparser.ConfigParser()
workdir = os.getcwd()

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
    subjectnamespacecolumn  = None
    allindexesareone = 1

    def __init__(self):
        try:
            parser.read('config.ini')
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exc())
            raise SystemExit
        self.targetAdress            = parser['targetRepo']['targetRepoAdress']
        self.targetAuthHeader        = parser['targetRepo']['targetAuthHeader']
        self.targetopenEHRAPIadress  = parser['targetRepo']['targetopenEHRAPIadress']
        self.targetflatAPIadress     = parser['targetRepo']['targetflatapiadress']
        self.templateName            = parser['DEFAULT']['templateName']
        self.inputCSV                = parser['DEFAULT']['inputCSV']
        self.createehrs              = parser['DEFAULT']['createehrs']
        self.directupload            = parser['DEFAULT']['directupload']
        self.subjectidcolumn         = parser['DEFAULT']['subjectidcolumn']
        self.subjectnamespacecolumn  = parser['DEFAULT']['subjectnamespacecolumn']
        self.allindexesareone        = parser['DEFAULT']['allindexesareone']

# Get AuthHeaders
def getAuthHeader(username, pw) -> str:
    """Return the base64 encoded auth header for a given username and passwort."""
    authHeader = "Basic " + base64.b64encode((username+":"+pw).encode('ascii')).decode()
    return authHeader

def readCSVasDataFrame(inputCSV):
    '''Read CSV as Dataframe'''
    # Compose Path
    csvPath = os.path.join(workdir, 'Input', inputCSV + '.csv')

    # Guess Encoding
    guessed_encoding = guessCSVencoding(csvPath)
    if guessed_encoding == 'windows-1255':
        guessed_encoding = "ANSI"

    # Read CSV-File  
    try: 
        dataDF = pd.read_csv(csvPath, header=0, delimiter=";", dtype = str, encoding = guessed_encoding)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

    return dataDF

def guessCSVencoding(filepath):
    # look at the first ten thousand bytes to guess the character encoding
    try:
        with open(filepath, 'rb') as rawdata:
            result = detect(rawdata.read(10000))
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

    return result['encoding']
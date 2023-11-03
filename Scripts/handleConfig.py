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
import csv
# Third party imports
import pandas as pd
from chardet import detect
# Local application imports

parser = configparser.ConfigParser()
workdir = os.getcwd()
config_path = os.path.join(workdir, 'config.ini')

class config():
    """ Represents a configparser-Config. Values are read from config.ini 
    
    Raises: 
        Catch-them-all Systemexit (on reading config.ini)
    """

    # Init mit Beispielwerten/Defaults
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
            config_file = open('config.ini', encoding="utf-8")
            parser.readfp(config_file)
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

def set_template_name(template_name):
    """Sets the Template-Name
    Args:
        templateName: Template-Name
    Returns:
        None
    """
    parser = configparser.ConfigParser()
    config_file = open('config.ini', encoding="utf-8")
    parser.read_file(config_file)
    parser.set(section="DEFAULT", option='templatename', value=template_name)
    config_file.close()  # Schließen Sie die Datei, nachdem Sie sie gelesen haben

    with open('config.ini', 'w', encoding="utf-8") as config_file:
        parser.write(config_file)

# Get AuthHeaders
def get_auth_header(username, pw) -> str:
    """ Computes Auth-Header in base64.

    Args:
      username: Username at the openEHR-CDR-Server
      pw: password for the user

    Returns:
      authHeader: Encoded in base64

    """
    authHeader = "Basic " + base64.b64encode((username+":"+pw).encode('ascii')).decode()
    return authHeader

def get_delimiter(file_path, bytes = 4096):
    """Determines the delimiter used in a file.

    Args:
      file_path: Path to the files that shall be analyzed
      bytes: (Default value = 4096)

    Returns:
      str: Delimiter-String

    """
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def read_csv_as_df(inputCSV):
    """Read CSV as Dataframe

    Args:
      inputCSV: CSV-File as Input

    Returns:
      Pandas-Dataframe: CSV as Dataframe

    Raises:
      Catch-them-all SystemExit
      
    """
    # Compose Path
    csvPath = os.path.join(workdir, 'ETLProcess', 'Input', inputCSV + '.csv')

    # Guess Encoding
    guessed_encoding = guess_csv_encoding(csvPath)
    if guessed_encoding == 'windows-1255':
        guessed_encoding = "ANSI"
    print(f"encoding is {guessed_encoding} for file with the path {csvPath}")
    # Read CSV-File  
    try: 
        dataDF = pd.read_csv(csvPath, header=0, delimiter=";", dtype = str, encoding = guessed_encoding) #";" # get_delimiter(csvPath)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

    return dataDF

def guess_csv_encoding(filepath):
    """ Tries to detect the encoding of a file by reading first 10k characters

    Args:
      filepath: Path to the file that shall be analyzed

    Returns:
      str: Encoding-String like (ANSI or UTF-8)

    Raises:
      Catch-them-all SystemExit

    """
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
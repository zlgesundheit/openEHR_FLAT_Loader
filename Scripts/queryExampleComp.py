#########################################################################
# Query Example Composition
#
# Via EHRBase FLAT API at {{host}}/rest/ecis/v1/template/:template_id/example?format=FLAT
# TODO: Query also Better-Example endpoint and see which on answers
# 
# Jendrik Richter (UMG)
#########################################################################

# Standard library imports
import os.path
import json
import requests
# Third party imports

# Local application imports
from Scripts import util

################################ Main #################################

def main():
    """ """
    pass  

############################### Methods ###############################

def query_example_composition(templateName, baseUrl, repo_auth):
    """Queries example composition from FLAT-API example endpoint of ehrbase.

    Args:
      baseUrl: 
      templateName: 
      repo_auth: 

    Returns:

    """
    url = f'{baseUrl}/rest/ecis/v1/template/{templateName}/example?format=FLAT'

    ##payload needs to be json! Otherwise it will just do nothin and run forever
    payload = {}

    headers = {
        'Authorization': repo_auth,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    exampleComp = json.loads(response.text)

    return exampleComp

def store_string_as_file(string, dirPath, filename):
    """Stores given string in specified directory with specified filename

    Args:
      string: param dirPath:
      filename: 
      dirPath: 

    Returns:
        None

    """
    filePath = os.path.join(dirPath, filename)
    with open(filePath,"w", encoding = 'UTF-8') as resFile:
        json.dump(string, resFile, default=util.convert, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
#########################################################################
# Build Example Composition
# Minimal Composition with only mandatory paths
# Maximal Composition with all Paths
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)
#########################################################################

# Standard library imports
import os.path
import json
import requests
# Third party imports
import numpy as np
# Local application imports
from Scripts import ucc_uploader

############################### Main ###############################

def main(workdir, pathArray, templateName, baseUrl, repo_auth, type):

    print ("BuildExampleComp started building Example Compositions")
    
    buildExample(workdir, pathArray, templateName, baseUrl, repo_auth, type)

    print ("Examples have been built and can be found in Output-Dir \n")

############################### Methods ###############################

# TODO Man koennte die If-Bedinung in die for-Schleife packen und damit Code-Zeilen einsparen, da Up/Download und Speichern für Min/Max gleich sind. Ist jetzt gerade aber anders gelaufen.
def buildExample(workdir, pathArray, templateName, baseUrl, repo_auth, type):
    # Create Example EHR
    ehrId = ucc_uploader.createNewEHRwithSpecificSubjectId(baseUrl, repo_auth, "examplePatient", "openEHR_FLAT_Loader")
    
    #Build Minimal Resource-Dict mit nur allen Pflichtpfaden
    if type == "min":
        dict = {}
        for path in pathArray:
            
            if path.isMandatory:
                # Dict["Pfad"] = valid Example-Value 
                if path.hasSuffix:
                    for suffix in path.suffixList:
                        dict[path.pathString + "|" + suffix] = path.exampleValue
                elif not path.hasSuffix:
                    dict[path.pathString] = path.exampleValue

        # Store FLAT Example-Composition
        filename = "MIN_EXAMPLE_FLAT_"+ templateName + ".json"
        storeStringAsFile(dict, workdir, filename)

        print ("\t" + f'FLAT Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

        # Upload FLAT Example-Comp
        flat_res = dict #json.dumps(dict)
        try:
            compId = ucc_uploader.uploadResourceToEhrId(baseUrl, repo_auth, ehrId, flat_res, templateName)
        except RuntimeError:
            print("Oops! Die Example-Composition wurde nicht erfolgreich hochgeladen.")
            raise SystemExit

        # Download Canonical Composition
        canonical_json = getCanonicalJSONComp(baseUrl, repo_auth, compId)

        # Store Canonical Composition
        filename = "MIN_EXAMPLE_CANONICAL_"+ templateName + ".json"
        storeStringAsFile(canonical_json, workdir, filename)

        print ("\t" + f'CANONICAL Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')
    #Build Maximal Resource-Dict mit allen Pfaden
    elif type == "max":
        #Build FLAT Maximal Resource-Dict mit allen Pfaden
        dict = {}
        for path in pathArray:
            # Im Maximal Example setze alle Indexe = 0
            path.pathString = path.pathString.replace("<<index>>", "0")

            # Pfade mit Suffixen und ohne dem CompositionDict hinzufügen
            if path.hasSuffix:
                for suffix in path.suffixList:
                    dict[path.pathString + "|" + suffix] = path.exampleValue
            elif not path.hasSuffix:
                dict[path.pathString] = path.exampleValue

        # Store Maximal FLAT Resource-Dict
        filename = "MAX_EXAMPLE_FLAT_"+ templateName + ".json"
        storeStringAsFile(dict, workdir, filename)

        print ("\t" + f'CANONICAL Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

        # Upload FLAT Maximal Composition
        flat_res = dict #json.dumps(dict)
        try:
            compId = ucc_uploader.uploadResourceToEhrId(baseUrl, repo_auth, ehrId, flat_res, templateName)
        except RuntimeError:
            print("Oops! Die Example-Composition wurde nicht erfolgreich hochgeladen.")
            raise SystemExit

        # Download CANONICAL Maximal Composition
        canonical_json = getCanonicalJSONComp(baseUrl, repo_auth, compId)

        # Store CANONICAL Maximal Composition 
        storeStringAsFile(canonical_json, workdir, "MAX_EXAMPLE_CANONICAL_"+ templateName + ".json")

        print ("\t" + f'CANONICAL Maximal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

def storeStringAsFile(string, workdir, filename):
    filePath = os.path.join(workdir, 'Output', filename)
    with open(filePath,"w", encoding = 'UTF-8') as resFile:
        json.dump(string, resFile, default=convert, indent=4, ensure_ascii=False)

def getCanonicalJSONComp(baseUrl, repo_auth, compId):
    '''Request to get a composition via rest/openehr/v1 Endpoint'''
    
    url = f'{baseUrl}/rest/ecis/v1/composition/{compId}?format=JSON'
    headers = {
    'Authorization' : repo_auth,
    }

    response = requests.get(url, headers=headers)

    # TODO Error Handling wenn response.status nicht in 200,201 oder anderen okayen..
    # Funktionaufruf dann in try-catch mit Ausgabe 
    # TODO Bei allenm Requests vernünftiges Exception-Handling :)

    response_text_json = json.loads(response.text)

    return response_text_json['composition']

# Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError
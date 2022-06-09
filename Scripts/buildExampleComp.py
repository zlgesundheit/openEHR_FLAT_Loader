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
import sys
import traceback
# Third party imports
import numpy as np
# Local application imports
from Scripts import handleUpload

############################### Main ###############################

def main(workdir, pathArray, templateName, baseUrl, repo_auth, type):

    print ("BuildExampleComp started building Example Compositions")
    
    outdir = os.path.join(workdir,'ExampleCompositions', templateName)
    if not os.path.isdir(outdir):
        createDir(outdir)
    buildExample(outdir, pathArray, templateName, baseUrl, repo_auth, type)

    print ("Examples have been built and can be found in Output-Dir \n")

############################### Methods ###############################

# TODO Man koennte die If-Bedinung in die for-Schleife packen und damit Code-Zeilen einsparen, da Up/Download und Speichern für Min/Max gleich sind. Ist jetzt gerade aber anders gelaufen.
def buildExample(outdir, pathArray, templateName, baseUrl, repo_auth, type):
    # Create Example EHR
    ehrId = handleUpload.createNewEHRwithSpecificSubjectId(baseUrl, repo_auth, "examplePatient", "openEHR_FLAT_Loader")
    
    #Build Minimal Resource-Dict mit nur allen Pflichtpfaden
    if type == "min":
        dict = {}
        for path in pathArray:
            if path.isMandatory:
                # Dict["Pfad"] = valid Example-Value 
                # TODO, hier testen, wenn ExampleDict in pathObject.py fertig ist.
                if not path.exampleValueDict == None:
                    exampleValueDict = path.exampleValueDict
                else:
                    print (f'Für Pfad {path.pathString} wurde kein Beispielwert generiert. -> ' + str(path.exampleValueDict))
                    raise RuntimeError
                
                for pfad in exampleValueDict:
                    if ('composer' in pfad and not '|name' in pfad) or ('subject' in pfad and not '|name' in pfad):
                        # Die EHRBASE hat (zumindest beim Composer) -> PARTY_PROXY nur |name als Pflicht. 
                        # Der Rest muss nicht vorhanden sein und sorgt für Fehler. Erstmal die anderen rausgenommen TODO
                        # Sprich |id, |id_scheme und |id_namespace werden ignoriert fuer das Beispiel
                        pass
                    else:
                        dict[pfad] = exampleValueDict[pfad]

        # Store FLAT Example-Composition
        filename = templateName + "-min_flat_example" + ".json"
        storeStringAsFile(dict, outdir, filename)

        print ("\t" + f'FLAT Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

        # Upload FLAT Example-Comp
        flat_res = dict #json.dumps(dict)
        try:
            compId = handleUpload.uploadResourceToEhrId(baseUrl, repo_auth, ehrId, flat_res, templateName)
        except RuntimeError:
            print("\tOops! Die Example-Composition wurde nicht erfolgreich hochgeladen.")
            raise SystemExit

        # Download Canonical Composition
        canonical_json = getCanonicalJSONComp(baseUrl, repo_auth, compId)

        # Store Canonical Composition
        filename = templateName + "-min_canonical_example"+ ".json"
        storeStringAsFile(canonical_json, outdir, filename)

        print ("\t" + f'CANONICAL Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')
    #Build Maximal Resource-Dict mit allen Pfaden
    elif type == "max":
        #Build FLAT Maximal Resource-Dict mit allen Pfaden
        dict = {}
        for path in pathArray:

            # Pfade mit Suffixen und ohne dem CompositionDict hinzufügen
            # TODO, hier testen, wenn ExampleDict in pathObject.py fertig ist.
            if not path.exampleValueDict == None:
                exampleValueDict = path.exampleValueDict
            else:
                # Bei Maximal-Komposition muessen alle Pfade vorkommen. Warum gibt es zu dem kein Example? Muesste schon vorher Fehler werfen.
                print (f'Für Pfad {path.pathString} wurde kein Beispielwert generiert. ->' + path.exampleValueDict)
                raise RuntimeError
            for pfad in exampleValueDict:
                if ('composer' in pfad and not '|name' in pfad) or ('subject' in pfad and not '|name' in pfad):
                    # Die EHRBASE hat (zumindest beim Composer) -> PARTY_PROXY nur |name als Pflicht. 
                    # Der Rest muss nicht vorhanden sein und sorgt für Fehler. Erstmal die anderen rausgenommen
                    # Sprich |id, |id_scheme und |id_namespace werden ignoriert fuer das Beispiel
                    pass
                else:
                    pfad_mit_index_0 = pfad.replace("<<index>>", "0") # Im Maximal Example setze alle Indexe = 0
                    dict[pfad_mit_index_0] = exampleValueDict[pfad]

        # Store Maximal FLAT Resource-Dict
        filename = templateName + "-max_flat_example" + ".json"
        storeStringAsFile(dict, outdir, filename)

        print ("\t" + f'CANONICAL Minimal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

        # Upload FLAT Maximal Composition
        flat_res = dict #json.dumps(dict)
        try:
            compId = handleUpload.uploadResourceToEhrId(baseUrl, repo_auth, ehrId, flat_res, templateName)
        except RuntimeError:
            print("\tOops! Die Example-Composition wurde nicht erfolgreich hochgeladen.")
            raise SystemExit

        # Download CANONICAL Maximal Composition
        canonical_json = getCanonicalJSONComp(baseUrl, repo_auth, compId)

        # Store CANONICAL Maximal Composition 
        storeStringAsFile(canonical_json, outdir, templateName + "-max_canonical_example" + ".json")

        print ("\t" + f'CANONICAL Maximal-Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

def storeStringAsFile(string, dirPath, filename):
    filePath = os.path.join(dirPath, filename)
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

def createDir(path):
    access_rights = 0o755
    try:
        os.mkdir(path, access_rights)
    except OSError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        print ("Creation of the directory %s failed" % path)
        raise SystemExit
    else:
        print ("Successfully created the directory %s" % path)
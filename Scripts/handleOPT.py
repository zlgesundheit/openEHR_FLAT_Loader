##################################################################
# Upload an OPT-File to an ehrscape-instance and an EHRBase
# Query a WebTemplate and an Example-Composition
#
# Jendrik Richter (UMG)
##################################################################
## Imports
# Standard library imports
import requests
import base64
import json
import os.path
# Third party imports
# Local application imports
from Scripts import pathExport
from Scripts import mappingListGen
from Scripts import configHandler

indent = "    "
workdir = os.getcwd()


############################### Main ###############################

def main():

    print(os.linesep + "Step 1: HandleOPT is running.")

    # Read Config
    config = configHandler.readConf()
    targetAdress            = config['targetRepo']['targetRepoAdress']
    targetAuthHeader        = config['targetRepo']['targetAuthHeader']
    targetopenEHRAPIadress  = config['targetRepo']['targetopenEHRAPIadress']
    targetflatAPIadress     = config['targetRepo']['targetflatapiadress']
    templateName            = config['DEFAULT']['templateName']
    inputCSV                = config['DEFAULT']['inputCSV']

    # Read OPT from Input Folder
    optFile = readOPTfromInput(templateName)

    # Upload OPT to server
    uploadOPT(templateName, optFile, targetAdress, targetopenEHRAPIadress, targetAuthHeader)

    # Query and save WebTemplate
    json_resp = queryWebtemplate(templateName, targetAdress, targetflatAPIadress, targetAuthHeader)

    #Store WebTemplate
    storeWebTemplate(templateName, json_resp)

    print(indent + "HandleOPT stored the WebTemplate.")

    # Get FLAT-Paths
    # Greife auf WebTemplate zu
    filePath = os.path.join(workdir, 'IntermFiles', templateName +'_WebTemplate.json')
    if os.path.isfile(filePath):
        # Lese WebTemplate ein
        webTemp = open(filePath, "r", encoding='utf-8').read()
        webTemp = json.loads(webTemp)
        # Extrahiere Pfade in Dict
        pathsDict = pathExport.main(webTemp, templateName)
    else:
        raise Exception(templateName + "_WebTemplate ist nicht vorhanden.")
    print(indent + "HandleOPT extracted FLAT-Paths from the WebTemplate")

    mappingListGen.main(templateName, inputCSV, pathsDict)
    print(indent + "HandleOPT generated the (empty) Mapping-Table")

############################### Methods ###############################

def readOPTfromInput(templateName):
    filePath = os.path.join(workdir, 'Input', 'OPT', templateName +'.opt')
    f = open(filePath, "r", encoding='utf-8')
    optFile = f.read()
    f.close()
    return optFile

# Get AuthHeaders
def getAuthHeader(user, pw):
  authHeader = base64.b64encode((user+":"+pw).encode('ascii'))
  authHeader = "Basic " + authHeader.decode()
  #print(authHeader)
  return authHeader

def uploadOPT(templateName, optFile, targetAdress, targetopenEHRAPIadress, targetAuthHeader):
    queryPath = targetAdress + targetopenEHRAPIadress + "definition/template/adl1.4"

    try:
        # Check if OPT is already present at the server
        respGet = requests.get(queryPath + "/" + templateName, headers = {'Authorization':targetAuthHeader})
        if respGet.status_code != 200:
            try:
                # Send OPT to Server
                response = requests.post(queryPath, headers = {'Authorization':targetAuthHeader, 'Content-Type':'application/xml', 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br'} ,data = optFile.encode('UTF-8')) 
                print (indent + "Template Upload to Target-Repo: " + os.linesep + indent + "Target-Repo: " + targetAdress + os.linesep + indent + "Status: " + str(response.status_code) )
            except Exception as e:
                print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
                raise SystemExit
        elif respGet.status_code == 200:
            print( indent + "OPT already exists at this server" )  

    except Exception as e:
        print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
        raise SystemExit

def queryWebtemplate(templateName, targetAdress, targetflatAPIadress, targetAuthHeader):
    queryPath = targetAdress + targetflatAPIadress + "template/" + templateName

    try:
        response = requests.get(queryPath, headers = {'Authorization':targetAuthHeader})
        json_resp = response.json()
    except Exception as e:
        print(indent + "Error while querying and saving WebTemplate from TargetRepo" + "\n" + indent + str(e))
        raise SystemExit

    return json_resp

def storeWebTemplate(templateName, json_resp):
    filePath = os.path.join(workdir, 'IntermFiles', templateName + '_WebTemplate.json')

    with open(filePath, 'w', encoding="utf-8") as templateFile:
        json.dump(json_resp['webTemplate'], templateFile, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    main()
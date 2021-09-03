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
from Scripts import mappingListGen as gen

indent = "    "

# Get AuthHeaders
def getAuthHeader(user, pw):
  authHeader = base64.b64encode((user+":"+pw).encode('ascii'))
  authHeader = "Basic " + authHeader.decode()
  #print(authHeader)
  return authHeader

def uploadOPT(targetAdress, targetopenEHRAPIadress, targetAuthHeader, optFile, templateName):
    queryPath = targetAdress + targetopenEHRAPIadress + "definition/template/adl1.4" 
    try:
        # Check if OPT is already present at the server
        respGet = requests.get(queryPath + "/" + templateName, headers = {'Authorization':targetAuthHeader})
        # print(respGet.status_code)
        if respGet.status_code != 200:
            try:
                # Send OPT to Server
                response = requests.post(queryPath, headers = {'Authorization':targetAuthHeader, 'Content-Type':'application/xml', 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br'} ,data = optFile.encode('UTF-8')) 
                print (indent + "Template Upload to Target-Repo: " + os.linesep + indent + "Target-Repo: " + targetAdress + os.linesep + indent + "Status: " + str(response.status_code) )
            except Exception as e:
                print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
                raise SystemExit
        else:
            print( indent + "OPT already exists at this server" )  
    except Exception as e:
        print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
        raise SystemExit

def queryWebtemplate(targetAdress, targetflatAPIadress, targetAuthHeader, templateName):
    workdir = os.getcwd()
    queryPath = targetAdress + targetflatAPIadress + "template/" + templateName
    try:
        response = requests.get(queryPath, headers = {'Authorization':targetAuthHeader})
        json_resp = response.json()
    except Exception as e:
        print(indent + "Error while querying and saving WebTemplate from TargetRepo" + "\n" + indent + str(e))
        raise SystemExit

    #Store WebTemplate
    filePath = os.path.join(workdir, 'IntermFiles', templateName + '_WebTemplate.json')
    with open(filePath, 'w', encoding="utf-8") as templateFile:
        json.dump(json_resp['webTemplate'], templateFile, indent = 4, ensure_ascii=False)

def handleOPT(templateName, inputCSV, targetAdress, targetAuthHeader, targetflatAPIadress, targetopenEHRAPIadress):
  print(os.linesep + "Step 1: HandleOPT is running.")
  workdir = os.getcwd()
  # Read OPT-File
  filePath = os.path.join(workdir, 'Input', 'OPT', templateName +'.opt')
  f = open(filePath, "r", encoding='utf-8')
  optFile = f.read()
  f.close()

  # Upload OPT to server
  uploadOPT(targetAdress, targetopenEHRAPIadress, targetAuthHeader, optFile, templateName)
  
  # Query and save WebTemplate
  queryWebtemplate(targetAdress, targetflatAPIadress, targetAuthHeader, templateName)
  
  # Get FLAT-Paths
  pathsDict = pathExport.getPathsFromWebTemplate(workdir, templateName)

  print(indent + "HandleOPT finished.")

  gen.generateList(templateName, inputCSV, pathsDict)

  answerString = ""
  return answerString

  

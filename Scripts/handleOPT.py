##################################################################
# Upload an OPT-File to an ehrscape-instance and an EHRBase
# Query a WebTemplate and an Example-Composition
#
# Jendrik Richter (UMG)
##################################################################
## Imports
# Standard library imports
import requests
import json
import os.path
# Third party imports
# Local application imports

indent = "\t"
workdir = os.getcwd()

############################### Main ###############################

def main(config):
    print("\nHandleOPT is running:")

    # Read OPT from Input Folder
    optFile = readOPTfromInput(config.templateName)

    # Upload OPT to server
    uploadOPT(config.templateName, optFile, config.targetAdress, config.targetopenEHRAPIadress, config.targetAuthHeader)

    # Query and save WebTemplate
    json_resp = queryWebtemplate(config.templateName, config.targetAdress, config.targetflatAPIadress, config.targetAuthHeader)

    # We load the webTemplate-Part of the Response in a nice tree structure
    webTemplateResp = json.dumps(json_resp['webTemplate'], ensure_ascii=False)
    webTemp = json.loads(webTemplateResp)

    print (indent + "OPT exists at server and WebTemplate has been downloaded")
    return webTemp

############################### Methods ###############################

def readOPTfromInput(templateName):
    """Read File with specific name from OPT-Folder"""
    filePath = os.path.join(workdir, 'Input', 'OPT', templateName +'.opt')
    try:
        f = open(filePath, "r", encoding='utf-8')
        optFile = f.read()
    finally:
        f.close()
    return optFile

def checkOPTExistence(templateName, queryPath, targetAuthHeader) -> int:
    """Query an Operational Template from specific openEHR-Repo and return Status Code"""
    try:
        # Check if OPT is already present at the server
        respGet = requests.get(queryPath + "/" + templateName, headers = {'Authorization':targetAuthHeader})
        return respGet.status_code
    except Exception as e:
        print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
        raise SystemExit

def uploadOPT(templateName, optFile, targetAdress, targetopenEHRAPIadress, targetAuthHeader) -> None:
    """Upload an Operational Template to a specific openEHR-Repo if it does not exist yet."""
    queryPath = targetAdress + targetopenEHRAPIadress + "definition/template/adl1.4"
    
    checkOPTExist_RespCode= checkOPTExistence(templateName, queryPath, targetAuthHeader)
    if  checkOPTExist_RespCode != 200:
        try:
            # Send OPT to Server
            response = requests.post(queryPath, headers = {'Authorization':targetAuthHeader, 'Content-Type':'application/xml', 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br'} ,data = optFile.encode('UTF-8')) 
            print (indent + "Template Upload to Target-Repo: " + os.linesep + indent + "Target-Repo: " + targetAdress + os.linesep + indent + "Status: " + str(response.status_code) )
        except Exception as e:
            print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
            raise SystemExit
    elif checkOPTExist_RespCode == 200:
        print( indent + "OPT already exists at this server" )

def queryWebtemplate(templateName, targetAdress, targetflatAPIadress, targetAuthHeader) -> str:
    """Query a webtemplate from a specific openEHR-Repo."""
    queryPath = targetAdress + targetflatAPIadress + "template/" + templateName
    try:
        response = requests.get(queryPath, headers = {'Authorization':targetAuthHeader})
        json_resp = response.json()
    except Exception as e:
        print(indent + "Error while querying and saving WebTemplate from TargetRepo" + "\n" + indent + str(e))
        raise SystemExit
    return json_resp

def storeWebTemplate(path, templateName, json_resp) -> None:
    """Store a JSON-String as a file"""
    filePath = os.path.join(workdir, path, templateName + '_WebTemplate.json')
    with open(filePath, 'w', encoding="utf-8") as templateFile:
        json.dump(json_resp['webTemplate'], templateFile, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    main()
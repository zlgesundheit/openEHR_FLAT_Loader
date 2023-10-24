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
import sys
import traceback
# Third party imports
# Local application imports

indent = "\t"
workdir = os.getcwd()

############################### Main ###############################

def main(config, manualTaskDir, OPTDirPath):
    print("\nHandleOPT is running:")

    # Read OPT from Input Folder
    optFile = read_local_opt(OPTDirPath, config.templateName)

    # Upload OPT to server
    upload_opt(config.templateName, optFile, config.targetAdress, config.targetopenEHRAPIadress, config.targetAuthHeader)

    webTemp = get_webtemplate(config, manualTaskDir)

    print (indent + "OPT exists at server and WebTemplate has been downloaded")
    return webTemp

############################### Methods ###############################

def get_webtemplate(config, manualTaskDir):
    # Query
    json_resp = query_webtemplate(config.templateName, config.targetAdress, config.targetflatAPIadress, config.targetAuthHeader)

    # We load the webTemplate-Part of the Response in a nice tree structure
    webTemplateResp = json.dumps(json_resp['webTemplate'], ensure_ascii=False)
    webTemp = json.loads(webTemplateResp)

    # Save WebTemplate to Manual Tasks Directory because it is so damn important for the mapping task
    store_webtemplate(manualTaskDir, config.templateName, webTemp)

    return webTemp

def read_local_opt(OPTDirPath, templateName):
    """Read File with specific name from OPT-Folder"""
    filePath = os.path.join(OPTDirPath, templateName +'.opt')
    try:
        f = open(filePath, "r", encoding='utf-8')
        optFile = f.read()
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
    finally:
        f.close()
    return optFile

def opt_exists(templateName, base, targetAuthHeader) -> int:
    """Query an Operational Template from specific openEHR-Repo and return Status Code"""
    
    try:
        # Check if OPT is already present at the server
        path = "definition/template/adl1.4/"
        url_plus = "".join([base,path,templateName])
        payload = {}
        headers = {'Authorization':targetAuthHeader}
        respGet = requests.request("GET", url_plus, headers=headers, data=payload)
        print("OP Exists? " + str(respGet.status_code))
        return respGet.status_code
    except:
        #print (respGet.status_code)
        #print (respGet.text)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

def upload_opt(templateName, optFile, targetAdress, targetopenEHRAPIadress, targetAuthHeader) -> None:
    """Upload an Operational Template to a specific openEHR-Repo if it does not exist yet."""
    base = targetAdress + targetopenEHRAPIadress
    
    checkOPTExist_RespCode= opt_exists(templateName, base, targetAuthHeader)
    if  checkOPTExist_RespCode != 200:
        try:
            # Send OPT to Server
            # print(base + "definition/template/adl1.4")
            response = requests.post(base + "definition/template/adl1.4", headers = {'Authorization':targetAuthHeader, 'Content-Type':'application/xml', 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br'} ,data = optFile.encode('UTF-8')) 
            print (indent + "Template Upload to Target-Repo: " + os.linesep + indent + "Target-Repo: " + targetAdress + os.linesep + indent + "Status: " + str(response.status_code) )
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exc())
            raise SystemExit
    elif checkOPTExist_RespCode == 200:
        print( indent + "OPT already exists at this server")

def query_webtemplate(templateName, targetAdress, targetflatAPIadress, targetAuthHeader) -> str:
    """Query a webtemplate from a specific openEHR-Repo."""
    queryPath = targetAdress + targetflatAPIadress + "template/" + templateName
    try:
        response = requests.get(queryPath, headers = {'Authorization':targetAuthHeader})
        if (response.status_code != 200):
            raise Exception(("Status Code: " + str(response.status_code)) + "\n " + indent + "Server-Message: " + response.text )
        json_resp = response.json()
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
    return json_resp

def store_webtemplate(manualTaskDir, templateName, webTemp) -> None:
    """Store a JSON-String as a file"""
    filePath = os.path.join(manualTaskDir, templateName + '_WebTemplate.json')
    try:
        with open(filePath, 'w', encoding="utf-8") as templateFile:
            json.dump(webTemp, templateFile, indent = 4, ensure_ascii=False)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

if __name__ == '__main__':
    main()
# Upload an OPT-File to an ehrscape-instance and an EHRBase
# Query a WebTemplate and an Example-Composition
#
# Jendrik Richter (UMG)

import requests
import base64
import json
import os.path
import re
import pathExport

indent = "    "

# Get AuthHeaders
def getAuthHeader(user, pw):
  authHeader = base64.b64encode((user+":"+pw).encode('ascii'))
  authHeader = "Basic " + authHeader.decode()
  #print(authHeader)
  return authHeader

def handleOPT(workdir, templateName, inputCSV, targetAdress, targetUser, targetPw, targetflatAPIadress, targetopenEHRAPIadress):
  print(os.linesep + "Step 1: HandleOPT is running.")
  targetAuth = getAuthHeader(targetUser, targetPw) 

  # Read OPT
  filePath = os.path.join(workdir, 'Input', templateName +'.opt')
  f = open(filePath, "r", encoding='utf-8')
  optFile = f.read()
  f.close()

  # Upload OPT to server
  queryPath = targetAdress + targetopenEHRAPIadress + "definition/template/adl1.4"
  authHeader = targetAuth
  try:
    # Setting the wrong headers may lead to the server storing the opt in a wrong encoding! Added Accept and Accept-Encoding to deal with this. We want UTF-8 # encoding the data-part did the trick
    response = requests.post(queryPath, headers = {'Authorization':authHeader, 'Content-Type':'application/xml', 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br'} ,data = optFile.encode('UTF-8')) 
    print (indent + "Template Upload to Target-Repo: " + os.linesep + indent + "Target-Repo: " + targetAdress + os.linesep + indent + "Status: " + str(response.status_code) )
  except Exception as e:
    print(indent + "Error while storing OPT at Target-Repo" + "\n" + indent + str(e) )
    raise SystemExit
  
  # Query and save WebTemplate
  queryPath = targetAdress + targetflatAPIadress + "template/" + templateName
  authHeader = targetAuth
  try:
    response = requests.get(queryPath, headers = {'Authorization':authHeader})
    json_resp = response.json()
  except Exception as e:
    print(indent + "Error while querying and saving WebTemplate from TargetRepo" + "\n" + indent + str(e))
    raise SystemExit

  filePath = os.path.join(workdir, 'Input', templateName + '_WebTemplate.json')
  f = open(filePath, 'w', encoding="utf-8")
  f.write( json.dumps(json_resp['webTemplate'], indent = 4) )
  f.close()
  

  pathsArray = pathExport.getPathsFromWebTemplate(workdir, templateName)

  print(indent + "HandleOPT finished.")

  import mappingListGen as gen
  gen.generateList(workdir, templateName, inputCSV, pathsArray)

  answerString = ""
  return answerString
  # Done

#######################################################
'''
# OLD PATH CAPTURE FROM EXAMPLE COMPOSITION
  # Read Composition-String from File (Example-Composition-String.json)
  exampleCompPath = os.path.join(workdir, 'Input', templateName + '_ExampleComp.json')
  f = open(exampleCompPath, "r")
  string = f.read()
  f.close()

  # Find all FLAT-Paths
  pattern = '\"[a-z,\/,_,|,:,0-9]*\":'
  pathsArray = re.findall(pattern, string)

  # Extract only path-Part of the Pathes
  count = 0
  for path in pathsArray:
    pathsArray[count] = path[1:-2]
    pathsArray[count] = pathsArray[count].replace('0', '<<index>>')
    count += 1
'''
#######################################################

  

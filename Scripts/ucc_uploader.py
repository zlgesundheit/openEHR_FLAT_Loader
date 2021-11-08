# Jendrik Richter

# Zweck: 
# Upload Ressourcen zu ehrID pro Fallkennung
# (Erster Aufschlag bzw. Quick and Dirty
#     -> Zweite Idee direkt bei der Erstellung der Ressourcen angeben lassen in welcher Spalte die patientenkennung/fallkennung steht 
#        und anschließend die ressource statt sie abzuspeichern direkt zu der ehrID hochladen)
#
# Some code and requests in Mareikes code

# POSTMAN
# Save Composition Anamnese
# http://141.5.100.115/ehrbase/rest/ecis/v1/composition/?format=FLAT&ehrId=59312ec0-d857-4c47-af59-86103040782f&templateId=Anamnese
# Header: 
#     Authorization = Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=   (for standard user on test ehrbase)
#     Content-Type = application/json
#     Accept-Encoding = gzip, deflate, br
# Body: 
#     json-resource
# Params:
#     format = FLAT
#     ehrId = z.B. 59312ec0-d857-4c47-af59-86103040782f
#     templateId = Anamnese     #KDS_Laborbefund
#     

#### Vorschritt
# ETL_Loader erzeugt Mapping
# Mapping wird manuelle befüllt
# Mapping erzeugt Ressourcen
# Ressourcen liegen im Output-Ordner

#############################################################################
# 1. Read patient_list 
# 2. Create ehrId for every patient
# 3. Create Map with ehrId <= sha1/kennung 
# 4. Read each resources and read the fallkennung of each resource and upload it to corresponding ehrId 

# ACHTUNG
# Not every resource has the fallkennung, right?? -> Put ehrId into the data and make an upload step in the tool instead of storing the resource locally...
# Haben alle Fall-Kennung, außer Person. Der Weg mit der ehrId in den Daten ist aber trotzdem besser..

# 5. Profit

from os import stat
import requests
#import grequests
# TODO parallelize requests using grequest -> install grequest in correct python kernel
import json
import numpy as np

# Can be found in Config.ini of ETL_Loader later
baseUrl = "http://141.5.100.115/ehrbase"
repo_auth = "Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=" ### unten auch zweimnal hardkodiert
targetflatapiadress = "/rest/ecis/v1/"
targetopenehrapiadress = "/rest/openehr/v1/"

def main():
    pass  

def uploadResourceToEhrIdFromCSV(baseUrl, csv_dataframe, resource, templateName, quick_and_dirty_index):
    'Wird dann in buildComp auffgerufen, liest hier die aktuelle CSV mit ehrIds ein' ### TODO ordentlich ins tool integrieren
    # Jede Zeile hat eine Ressource. Das ResourceDict (das in Build-Comp durchlaufen wird) entspricht also den indexen der CSV
    # Quick and Dirty nimm einen index entgegen und lade Ressource "x" hoch zu csv_dataframe[ehrId][x]
    ehrId = csv_dataframe['ehrId'][quick_and_dirty_index]

    url = f'{baseUrl}/rest/ecis/v1/composition/?format=FLAT&ehrId={ehrId}&templateId={templateName}'

    ##payload needs to be json! Otherwise it will just do nothin and run forever
    payload = json.dumps(resource, default=convert)

    print (payload)

    headers = {
        'Authorization': repo_auth,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    #response = requests.post(url, data=payload, headers=headers)
    response = requests.request("POST", url, headers=headers, data=payload, timeout = 15)

    print ("Status beim Upload der Composition: " + str(response.status_code))
    print (response.text)
    
# for numpy int in pandas df 
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def createEHRsForAllPatients(csv_dataframe, patient_id_column_name, subject_namespace_column_name):
    '''Nimmt CSV und Spaltenname der identifizierenden ID / Primaerschluessel des Datensatzes entgegen, um fuer jeden Patienten ein EHR zu erstellen.
       Ein Check, ob die EHR zu der ID bereits existiert ist notwendig.
    '''
    for index in csv_dataframe.index:   ## TODO LATER make a cool apply+lambda to read subject id and subject_namespace per row and make things. For now use 
        # Try to retrieve existing ehr by "subject id" and "subject namespace" 
        subject_id = csv_dataframe[patient_id_column_name][index]
        subject_namespace = csv_dataframe[subject_namespace_column_name][index]

        ### TODO LATER: Maybe while creating an already existing ehr / subject_id the server will state that it already exist. Would save time

        # Create ehr with subject id = identifizierenden ID und subject namespace = z.B. "ucc_sha1_h_dathe"
        ehrId = createNewEHRwithSpecificSubjectId(baseUrl,subject_id, subject_namespace)
        csv_dataframe['ehrId'][index] = ehrId

    return csv_dataframe

def createNewEHRwithSpecificSubjectId(baseUrl, subject_id, subject_namespace):
    url = f'{baseUrl}/rest/openehr/v1/ehr'
    
    payload = json.dumps({
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {
            "value": "EHR"
        },
        "subject": {
            "external_ref": {
            "id": {
                "_type": "GENERIC_ID",
                "value": subject_id,
                "scheme": "id_scheme"
            },
            "namespace": subject_namespace,
            "type": "PERSON"
            }
        },
        "is_modifiable": True,
        "is_queryable": True
    })

    header = {
        'Authorization' : "Basic ZWhyYmFzZS11c2VyOmVuVGluVEFuZ2xBSw==",
        'Content-Type': 'application/json',
        'Prefer' : 'return=representation'
    }

    response = requests.post(url, data=payload, headers=header)

    if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
        response_dict = json.loads(response.text)
        ehrId = response_dict['ehr_id']['value']
        print ("    " + "Created EHR with ehrID: " + ehrId)
    else:
        print ("    " + "Fehler beim EHR erstellen mit Status: " + str(response.status_code))
        ehrId = None
        pass

    return ehrId

if __name__ == '__main__':
    main()
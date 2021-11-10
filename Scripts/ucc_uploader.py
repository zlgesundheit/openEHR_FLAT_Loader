# Jendrik Richter

# Zweck: 
# Upload Ressourcen zu ehrID pro Fallkennung
# (Erster Aufschlag bzw. Quick and Dirty
#     -> Zweite Idee direkt bei der Erstellung der Ressourcen angeben lassen in welcher Spalte die patientenkennung/fallkennung steht 
#        und anschließend die ressource statt sie abzuspeichern direkt zu der ehrID hochladen)

from os import stat
import requests
#import grequests
# TODO parallelize requests using grequest -> install grequest in correct python kernel
import json
import numpy as np

def main():
    pass  

def uploadResourceToEhrIdFromCSV(baseUrl, repo_auth, csv_dataframe, resource, templateName, quick_and_dirty_index):
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
    response = requests.post(url, headers=headers, data=payload) #, timeout = 15)

    print ("Status beim Upload der Composition: " + str(response.status_code))
    print (response.text)
    
# for numpy int in pandas df 
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def createEHRsForAllPatients(baseUrl, repo_auth, csv_dataframe, patient_id_column_name, subject_namespace_column_name):
    '''Nimmt CSV und Spaltenname der identifizierenden ID / Primaerschluessel des Datensatzes entgegen, um fuer jeden Patienten ein EHR zu erstellen.
       Ein Check, ob die EHR zu der ID bereits existiert ist notwendig.
    '''
    for index in csv_dataframe.index:   ## TODO LATER make a cool apply+lambda to read subject id and subject_namespace per row and make things. For now use 
        # Try to retrieve existing ehr by "subject id" and "subject namespace" 
        subject_id = csv_dataframe[patient_id_column_name][index]
        subject_namespace = csv_dataframe[subject_namespace_column_name][index]

        ### TODO LATER: Maybe while creating an already existing ehr / subject_id the server will state that it already exist. Would save time

        # Create ehr with subject id = identifizierenden ID und subject namespace = z.B. "ucc_sha1_h_dathe"
        ehrId = createNewEHRwithSpecificSubjectId(baseUrl, repo_auth, subject_id, subject_namespace)
        # TODO Was tun falls die ehrId schon existiert
        if not ehrId is None:
            csv_dataframe['ehrId'][index] = ehrId
        else:
            pass

    return csv_dataframe

def createNewEHRwithSpecificSubjectId(baseUrl, repo_auth, subject_id, subject_namespace):
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

    headers = {
        'Authorization' : repo_auth,
        'Content-Type': 'application/json',
        'Prefer' : 'return=representation'
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
        response_dict = json.loads(response.text)
        ehrId = response_dict['ehr_id']['value']
        print ("    " + "Created EHR with ehrID: " + ehrId)
    else:
        print ("    " + "Fehler beim EHR erstellen mit Status: " + str(response.status_code))
        # ehrId zu dem Subject abfragen -> Warum zur Hölle gibt der Konflikt eine PartyId die sich nirgend wiederfindet und ich muss nochmal abfragen..
        
        url = f'{baseUrl}/rest/openehr/v1/ehr?subject_id={subject_id}&subject_namespace={subject_namespace}'
        headers = {
        'Authorization' : repo_auth,
        'Content-Type': 'application/json',
        'Prefer' : 'return=representation'
        }

        response_bei_conflict = requests.get(url, headers=headers)
        
        response_dict = json.loads(response_bei_conflict.text)
        ehrId = response_dict['ehr_id']['value']
        print ("\t EHR existierte bereits mit ehrID: " + ehrId)

    return ehrId

if __name__ == '__main__':
    main()
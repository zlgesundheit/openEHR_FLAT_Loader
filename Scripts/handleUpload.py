# Jendrik Richter

# Zweck: 
# Upload Ressourcen zu ehrID pro Fallkennung
# (Erster Aufschlag bzw. Quick and Dirty
#     -> Zweite Idee direkt bei der Erstellung der Ressourcen angeben lassen in welcher Spalte die patientenkennung/fallkennung steht 
#        und anschließend die ressource statt sie abzuspeichern direkt zu der ehrID hochladen)

import os
import sys
import traceback
import requests
#import grequests
# TODO parallelize requests using grequest -> install grequest in correct python kernel -> Ist das notwendig. 
# ----> Performancetests von Luca abwarten. EHRBase geht evtl in die Knie bei gleichzeitigen Anfragen :D
import json
import numpy as np

def main():
    pass  

def upload_comp_to_ehrid(baseUrl, repo_auth, ehrId, resource, templateName, comp_created_count):
    
    url = f'{baseUrl}/rest/ecis/v1/composition/?format=FLAT&ehrId={ehrId}&templateId={templateName}'

    ##payload needs to be json! Otherwise it will just do nothin and run forever
    payload = json.dumps(resource, default=convert)

    headers = {
        'Authorization': repo_auth,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    try:
        #response = requests.post(url, headers=headers, data=payload) #, timeout = 15)
        response = requests.request("POST", url, headers=headers, data=payload)
        
        resp_json = json.loads(response.text)
        print ("\n    Status beim Upload der Composition: " + str(response.status_code))
        print ("\t"+str(resp_json))
        print ("\t" + "CompositionUid: " + resp_json["compositionUid"] + "\n")

        if response.status_code == 201:
            comp_created_count +=1

        return resp_json["compositionUid"], comp_created_count
        
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

# for numpy int in pandas df 
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

def createEHRsForAllPatients(baseUrl, repo_auth, csv_dataframe, patient_id_column_name, subject_namespace_column_name, ehr_counter):
    """Nimmt CSV und Spaltenname der identifizierenden ID / Primaerschluessel des Datensatzes entgegen, um fuer jeden Patienten ein EHR zu erstellen.
       Ein Check, ob die EHR zu der ID bereits existiert ist notwendig."""
    for index in csv_dataframe.index:   ## TODO LATER make a cool apply+lambda to read subject id and subject_namespace per row and make things. For now use 
        # Try to retrieve existing ehr by "subject id" and "subject namespace" 
        subject_id = csv_dataframe[patient_id_column_name][index]
        subject_namespace = csv_dataframe[subject_namespace_column_name][index]

        # Create ehr with subject id = identifizierenden ID und subject namespace = z.B. "ucc_sha1_h_dathe"
        ehr_id = create_ehr_with_specific_subjectid(baseUrl, repo_auth, subject_id, subject_namespace)
        csv_dataframe['ehrId'][index] = ehr_id
        if (ehr_id != None):
            ehr_counter += 1

    return csv_dataframe, ehr_counter

def create_ehr_with_specific_subjectid(baseUrl, repo_auth, subject_id, subject_namespace):
    url = f'{baseUrl}/rest/openehr/v1/ehr'
    
    payload = json.dumps({
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {"value": "EHR"},
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
        'Content-type': 'application/json',
        'Prefer' : 'return=representation',
    }

    #response = requests.post(url, data=payload, headers=headers)
    response = requests.request("POST", url, headers=headers, data=payload)
    '''
    try:
        response = requests.post(url, data=payload, headers=headers)
        print (response.statusCode)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(response.statusCode)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
    '''
    if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
        response_dict = json.loads(response.text)
        ehrId = response_dict['ehr_id']['value']
        print ("\t" + "Created EHR with ehrID: " + ehrId)
    else:
        print ("    " + "Hindernis beim EHR erstellen mit Status: " + str(response.status_code))
        # ehrId zu dem Subject abfragen -> Warum zur Hölle gibt der Konflikt eine PartyId die sich nirgend wiederfindet und ich muss nochmal abfragen..
        
        url = f'{baseUrl}/rest/openehr/v1/ehr?subject_id={subject_id}&subject_namespace={subject_namespace}'
        headers = {
        'Authorization' : repo_auth,
        'Content-Type': 'application/json',
        'Prefer' : 'return=representation'
        }
        
        #try:
        response_bei_conflict = requests.get(url, headers=headers)
    
        response_dict = json.loads(response_bei_conflict.text)
        ehrId = response_dict['ehr_id']['value']
        print ("      EHR existierte bereits mit ehrID: " + ehrId + "\n")
        #except:
        #    exc_type, exc_obj, exc_tb = sys.exc_info()
        #    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #    print(exc_type, fname, exc_tb.tb_lineno)
        #    print(traceback.format_exc())
        #    raise SystemExit

    return ehrId

if __name__ == '__main__':
    main()
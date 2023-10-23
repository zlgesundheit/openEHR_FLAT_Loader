# Context: Use Case Cardiology from HiGHmed
# Environment: Better Repo (Only relevant for AQL-Syntax)
#
# Developed and tested with Python 3.10.4
#
# Jendrik Richter (UMG)
#########################################################################

import os.path
import sys
import re
import requests
import traceback

from Scripts import handleWebTemplate

import json
import csv
import pandas as pd

def find_quantity_value(obj):
    # Check if obj is a dictionary
    if isinstance(obj, dict):
        # Check if the dictionary has "_type" key set to "DV_QUANTITY" and contains both "magnitude" and "units" keys
        if "_type" in obj and obj["_type"] == "DV_QUANTITY" and "magnitude" in obj and "units" in obj:
            # Return the combination of "magnitude" and "units"
            return obj["magnitude"], obj["units"]
    return None

def find_named_value(obj):
    """TODO: Check what is meant by 'named'-value"""
    # Check if obj is a dictionary
    if isinstance(obj, dict):
        # Iterate through key-value pairs in the dictionary
        for key, value in obj.items():
            # Check if the current key is "value" or "name"
            if key == "value" or key == "name":
                # If the key is "value" or "name," return the associated value
                return value
            # If the value is a dictionary or a list, recursively call the function
            elif isinstance(value, (dict, list)):
                result = find_named_value(value)
                if result is not None:
                    return result
    return None

def find_value(obj):
    # Check if obj is a dictionary
    if isinstance(obj, dict):
        # Call find_quantity_value to check for DV_QUANTITY and return its value
        quantity_value = find_quantity_value(obj)
        if quantity_value is not None:
            return quantity_value
        # Call find_named_value to search for "value" or "name" and return its value
        named_value = find_named_value(obj)
        if named_value is not None:
            return named_value
    # Check if obj is a list
    elif isinstance(obj, list):
        # Iterate through list items and recursively call the function
        for item in obj:
            result = find_value(item)
            if result is not None:
                return result
    # If no matching values are found, return None to indicate that the value was not found
    return None



def process_rows(all_compositions_as_list, column_names):
    '''TODO: Rename function and variables and comment'''
    all_compositions_as_df = pd.DataFrame(all_compositions_as_list, columns=column_names)
    for index, composition in all_compositions_as_df.iterrows():
        for col in composition.index:
            if isinstance(composition[col], dict):
                value = find_value(composition[col])
                if value is not None:
                    if isinstance(value, tuple):
                        all_compositions_as_df.rename(columns={col: f"{col} (in {value[1]})"}, inplace=True)
                        composition[col] = value[0]
                    else:
                        composition[col] = value
    return all_compositions_as_df

def storeRespAsCSV(workdir, subfolder, resp, filename, web_temp_elmnts):
    # Get Lists of Column-Names and Rows
    column_names = []
    for elmnt in resp.get('columns'):
        name_elmnt_webtemplate = handleWebTemplate.map_aql_path_and_id_of_path_object(web_temp_elmnts, elmnt['path'])
        column_names.append(name_elmnt_webtemplate)

    rows = resp.get('rows')
    processed_rows = process_rows(rows, column_names)

    # Store DF as CSV
    path_to_store = os.path.join(workdir, subfolder)
    if not os.path.exists(path_to_store):
        print(f"Create Folder {path_to_store}")
        os.makedirs(path_to_store)
    processed_rows.to_csv(os.path.join(path_to_store, filename), encoding="utf-8", index = False, quoting=csv.QUOTE_ALL, sep=";")
    print(f"Stored File {filename} in Folder {path_to_store}")

def sendAqlRequest(ehrUrl, authHeader, limit, aqlQuery):

    payload = json.dumps({
        "q": aqlQuery,
        "offset": 0,
        "fetch": limit,
        "limit":limit
    })

    headers = {
        'Authorization' : authHeader,
        'Content-type': 'application/json',
        'Prefer' : 'return=representation',
    }
    try:
        response = requests.request("POST", ehrUrl + "/rest/openehr/v1/query/aql", headers=headers, data=payload)

        if response.status_code == 200:
            resp_json = json.loads(response.text)
            return resp_json
        else:
            resp_json = json.loads(response.text)
            print(resp_json)
            return None

    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit

def readFile(dirPath, filename):
    """Read File with specific name from path"""
    filePath = os.path.join(dirPath, filename)
    try:
        f = open(filePath, "r", encoding='utf-8')
        file = f.read()
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        raise SystemExit
    finally:
        f.close()
    return file

def load_env_file(dotenv_path, override=False):
    with open(dotenv_path) as file_obj:
        lines = file_obj.read().splitlines()  # Removes \n from lines

    dotenv_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        #value = value[1:] #strips first = char from string
        dotenv_vars.setdefault(key, value)

    if override:
        os.environ.update(dotenv_vars)
    else:
        for key, value in dotenv_vars.items():
            os.environ.setdefault(key, value)

def remove_and_statements(input_string):
    # Regex-Pattern zum Ersetzen von " and ..." durch "]"
    pattern = r' and [^\]]*\''
    adjusted_string = re.sub(pattern, "",input_string)
    return adjusted_string
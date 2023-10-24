# Context: Use Case Cardiology from HiGHmed
# Environment: Better Repo (Only relevant for AQL-Syntax)
#
# Developed and tested with Python 3.10.4
#
# Jendrik Richter and Lennart Graf (UMG)
#########################################################################

import os.path
import sys
import re
import requests
import traceback

from Scripts import handleWebTemplate, handleConfig

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

def find_code_phrase_value(obj):
    t=1
    # Check if obj is a dictionary
    if "_type" in obj and obj["_type"] == "DV_CODED_TEXT":
        return find_code_phrase_value(obj["defining_code"])
    if isinstance(obj, dict) or isinstance(obj, pd.Series):
        # Check if the dictionary has "_type" key set to "CODE_PHRASE" and contains "code" and "terminology"
        if "_type" in obj and obj["_type"] == "CODE_PHRASE" and "code_string" in obj and "terminology_id" in obj:
            # Return the combination of "code" and "terminology"
            return obj["code_string"]
    return None

def find_named_value(obj):
    # Check if obj is a dictionary
    if isinstance(obj, dict):
        # Iterate through key-value pairs in the dictionary
        for key, value in obj.items():
            # Check if the current key is "value" or "name" or "magnitude"
            if key == "value" or key == "name" or key == "magnitude":
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
    if isinstance(obj, dict) or isinstance(obj, pd.Series):
        # Call find_quantity_value to check for DV_QUANTITY and return its value
        code_phrase_value = find_code_phrase_value(obj)
        if code_phrase_value is not None:
            return code_phrase_value
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
    all_compositions_as_df = rename_duplicate_columns(all_compositions_as_df)
    for index, composition in all_compositions_as_df.iterrows():
        composition = pd.Series(composition)

        for index, col in composition.items():
            if index == "language":
                test=1
            if isinstance(col, dict) or isinstance(col, pd.Series):
                value = find_value(col)
                if value is not None:
                    if isinstance(value, tuple):
                        all_compositions_as_df.rename(columns={index: f"{index} (in {value[1]})"}, inplace=True)
                        composition[index] = value[0]
                    else:
                        composition[index] = value
    return all_compositions_as_df
def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + str(i + 1) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df


def store_resp_as_csv(workdir, subfolder, resp, filename, web_temp_elmnts):
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
    processed_rows.to_csv(os.path.join(path_to_store, filename), encoding="UTF-8", index = False, quoting=csv.QUOTE_ALL, sep=";")
    print(f"Stored File {filename} in Folder {path_to_store}")

def send_aql_request(ehrUrl, authHeader, limit, aqlQuery):

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

def read_file(dirPath, filename):
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

def get_templates_from_server(config: handleConfig.config) -> list:
    """Querys all templates distinct from the given server in the config, which contain a compositions"""
    aql_string = "SELECT DISTINCT c/archetype_details/template_id/value as TemplateID FROM EHR e CONTAINS COMPOSITION c"
    all_templates = send_aql_request(config.targetAdress, config.targetAuthHeader, "9999999999999", aql_string)
    flat_list_all_templates = [item for sublist in all_templates["rows"] for item in sublist]
    return flat_list_all_templates
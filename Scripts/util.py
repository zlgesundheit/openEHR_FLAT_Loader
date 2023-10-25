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
import numpy as np

def find_quantity_value(obj):
    """

    Args:
      obj: 

    Returns:

    """
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
    """

    Args:
      obj: 

    Returns:

    """
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
    """

    Args:
      obj: 

    Returns:

    """
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



def transform_rows_from_compositions_to_dataframe(rows_from_compositions_as_list, column_names):
    """
    Args:
      rows_from_compositions_as_list: All rows of a composition giving back by the server
      column_names: the actual column names of the entries in the list

    Returns:
      processed_dataframe: transformed rows of compositions to dataframe
    """
    processed_dataframe = pd.DataFrame(rows_from_compositions_as_list, columns=column_names)
    processed_dataframe = rename_duplicate_columns(processed_dataframe)
    for index, composition in processed_dataframe.iterrows():
        composition = pd.Series(composition)
        for column_name, column_content in composition.items():
            if isinstance(column_content, dict) or isinstance(column_content, pd.Series):
                value = find_value(column_content)
                if value is not None:
                    if isinstance(value, tuple):
                        unit = value[1]
                        new_col_name = f"Unit for column '{column_name}'"

                        # Adds the new column if it does not already exist
                        # Position of the new unit-column: 1 after the value column
                        if new_col_name not in processed_dataframe.columns:
                            processed_dataframe.insert(processed_dataframe.columns.get_loc(column_name)
                                                          + 1, new_col_name, unit)

                        # Update the values in the new column
                        processed_dataframe.at[index, new_col_name] = unit
                        composition[column_name] = value[0]
                    else:
                        composition[column_name] = value
    return processed_dataframe
def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + str(i + 1) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df


def store_resp_as_csv(workdir, subfolder, resp, filename, web_temp_elmnts):
    """

    Args:
      workdir: param subfolder:
      resp: param filename:
      web_temp_elmnts: param subfolder:
      filename: 
      subfolder: 

    Returns:

    """
    # Get Lists of Column-Names and Rows
    column_names = []
    for elmnt in resp.get('columns'):
        name_elmnt_webtemplate = handleWebTemplate.map_aql_path_and_id_of_path_object(web_temp_elmnts, elmnt['path'])
        column_names.append(name_elmnt_webtemplate)

    rows = resp.get('rows')
    processed_rows = transform_rows_from_compositions_to_dataframe(rows, column_names)

    # Store DF as CSV
    path_to_store = os.path.join(workdir, subfolder)
    if not os.path.exists(path_to_store):
        print(f"Create Folder {path_to_store}")
        os.makedirs(path_to_store)
    processed_rows.to_csv(os.path.join(path_to_store, filename), encoding="UTF-8", index = False, quoting=csv.QUOTE_ALL, sep=";")
    print(f"Stored File {filename} in Folder {path_to_store}")

def send_aql_request(ehrUrl, authHeader, limit, aqlQuery):
    """

    Args:
      ehrUrl: param authHeader:
      limit: param aqlQuery:
      authHeader: param aqlQuery:
      aqlQuery: 

    Returns:

    """

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
    """Read File with specific name from path

    Args:
      dirPath: param filename:
      filename: 

    Returns:

    """
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
    """

    Args:
      dotenv_path: param override:  (Default value = False)
      override: Default value = False)

    Returns:

    """
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

def remove_and_statements(aql_path):
    """

    Args:
      aql_path: aql path which contains a 'and statement'

    Returns:
      adjusted_string: aql_path without 'and statement'
    """
    # Regex-Pattern zum Ersetzen von " and ..." durch "]"
    pattern = r' and [^\]]*\''
    adjusted_string = re.sub(pattern, "",aql_path)
    return adjusted_string

def get_templates_from_server(config: handleConfig.config) -> list:
    """Querys all templates distinct from the given server in the config, which contain a compositions

    Args:
      config: handleConfig.config:
      config: handleConfig.config:
      config: handleConfig.config:
      config: handleConfig.config: 

    Returns:

    """
    aql_string = "SELECT DISTINCT c/archetype_details/template_id/value as TemplateID FROM EHR e CONTAINS COMPOSITION c"
    all_templates = send_aql_request(config.targetAdress, config.targetAuthHeader, "9999999999999", aql_string)
    flat_list_all_templates = [item for sublist in all_templates["rows"] for item in sublist]
    return flat_list_all_templates

def store_string_as_file(string, dirPath, filename):
    """Stores given string in specified directory with specified filename

    Args:
      string: param dirPath:
      filename: 
      dirPath: 

    Returns:
        None

    """
    filePath = os.path.join(dirPath, filename)
    with open(filePath,"w", encoding = 'UTF-8') as resFile:
        json.dump(string, resFile, default=convert, indent=4, ensure_ascii=False)

# Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)
def convert(o):
    """Helper function that converst panda data types that are not serializable

    Args:
      o: pandas int that is not serializable

    Returns:
      int64: Given item as np.int64

    Raises:
      TypeError
    """
    if isinstance(o, np.int64): return o.item()  
    raise TypeError

# TODO Unused at the moment
def get_comp_by_compid(baseUrl, repo_auth, compId):
    """Request to get a composition via rest/openehr/v1 Endpoint

    Args:
      baseUrl: Host-URL
      compId: Composition ID
      repo_auth: Auth-Header (base64) username:password

    Returns:
      composition as string
    """
    
    url = f'{baseUrl}/rest/ecis/v1/composition/{compId}?format=JSON'
    headers = {
    'Authorization' : repo_auth,
    }

    response = requests.get(url, headers=headers)

    # TODO Error Handling wenn response.status nicht in 200,201 oder anderen okayen..

    response_text_json = json.loads(response.text)

    return response_text_json['composition']
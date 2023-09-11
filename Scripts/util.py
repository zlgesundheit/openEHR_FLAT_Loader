# Context: Use Case Cardiology from HiGHmed
# Environment: Better Repo (Only relevant for AQL-Syntax)
#
# Developed and tested with Python 3.10.4
#
# Jendrik Richter (UMG)
#########################################################################

import os.path
import sys
import requests
import traceback

import json
import csv
import pandas as pd

def storeRespAsCSV(workdir, subfolder, resp, filename):
    # Get Lists of Column-Names and Rows
    column_names = []
    for elmnt in resp.get('columns'):
        column_names.append((elmnt['path']))

    rows = resp.get('rows')

    # Create Pandas DF from Lists
    df = pd.DataFrame(rows, columns=column_names)

    # Store DF as CSV
    df.to_csv(os.path.join(workdir, subfolder, filename), encoding="utf-8", index = False, quoting=csv.QUOTE_ALL)
    print(f"Stored File {filename} in Folder csv_input")

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
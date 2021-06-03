# openEHR_FLAT_Loader

ETL-Tool to transform Source Data into openEHR-Resources.  

## Usage
1. Place your .OPT-File in the Input-Folder
2. Run Tool via Command Line with `python runMain.py`
    - If the config-file is not presented you will be asked to provide infos. 
    - It is of course also possible to adjust them directly in the config-file 
      - -> See [Config-File](#config-file)
    - You will be asked which step of the process you want to perform
        - Step 1: Upload OPT and generate Mapping-(Excel-)File
        - Step 2: Build Compositions based on the Mapping
3. To perform Step 2: Building Compositions you have to supply mapping information in the Mapping-Table
4. After performing Step 2 you will find the FLAT-Composition in the Output-Folder 

## Context
To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources a ETL-Job - for a specific Template / Operational Template - has to be built.  
The idea of [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4) as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resource using a Mapping (manuall supplied by the user) from DataFields to TemplateFields.

_Process-Overview:_

![BPMN-Process-Overview](/Dokumentation/Process_Overview_Screenshot.jpg)

_Prerequisites:_
- Project was developed and tested using Python 3.8.3
- An openEHR-Repo with the endpoints to supply a WebTemplate and to store Resources in FLAT-Format

## Config-File
- The `.config.ini` holds the following information:

    **Environment Infos:**
    | config-variable | Description |
    | --------------- | ------ |
    | workdir         | Working Directory (e.g. `C:\Users\richter122\git-projects\openehr_flat_loader`) |
    | templatename    | Name of the Template (e.g. `UMG_Stammdaten`) |
    | inputcsv        | Name of the csv-file that holds the data (`source_data`) |
    
    **Repository Infos:**
    | config-variable | Description |
    | --------------- | ------ |
    | targetrepoadress| Baseadress of the Target Repo (e.g. `http://141.5.100.199/ehrbase`) |
    | targetrepouser  | Username for authentification with the Repo (e.g. `ehrbase-user`) |
    | targetrepopw    | Password for authentification with the Repo (e.g. `SuperSecretPassword`) |
    | targetflatapiadress | The endpoint where the FLAT-API resides (e.g. `/rest/ecis/v1/`) |
    | targetopenehrapiadress| The endpoint where the openEHR-API resides (e.g. `/rest/openehr/v1/`)|

## Work in Progress:
- SQL-DB as Data Source? Let User provide a query and get data from there
- GUI with good Usability

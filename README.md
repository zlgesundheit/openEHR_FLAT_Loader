# openEHR_FLAT_Loader

ETL-Tool to transform Source Data into openEHR-Resources.  

## Manual
A guide on how to use the tool and explaination of the context (openEHR, data curation) is currently under development.
The manual can be found [here](/Dokumentation/MANUAL_openEHR_FLAT_Loader.md) and is located in the "Documentation" folder.

-- Work in Progress --

## _Prerequisites:_
- Project was developed and tested using Python 3.8.10 with "openpyxl" and "requests"
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates (e.g. [EHRBase](https://github.com/ehrbase/ehrbase))
    - Dockered version of the EHRBase can be found from different public sources or [here](https://gitlab.gwdg.de/medinf/ivf/zukunftslabor-gesundheit/zlg-ehrbase/-/tree/zl-prod).

## Usage
1. Place your .OPT-File in the Input-Folder
2. Run Tool using the runFlatLoader_win.bat on Windows or runFlatLoader_lin.sh if you are on Linux.
   If you use a MAC try starting the runMain.py in Scripts-Directory...
    - If the config-file is not existing you will be asked to provide some config-settings. 
    - It is also possible to adjust these settings directly in the config-file 
      - -> See [Config-File](#config-file)
    - You will be asked which step of the process you want to perform
        - Step 1: Upload OPT and generate Mapping-(Excel-)File
3. To build build Compositions you have to supply mapping information in the Mapping-Table and save the Excel-file
4. Run the tool again and perform step 2:
	- Step 2: Build Compositions based on the Mapping
4. After performing Step 2 you will find the FLAT-Composition in the Output-Folder 

## Context
To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources a ETL-Job - for a specific Template / Operational Template - has to be built.  
The idea of [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4) as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resource using a Mapping (manually supplied by the user) from DataFields to TemplateFields.

_Process-Overview:_

![BPMN-Process-Overview](/Dokumentation/Figures/Process_Overview_Screenshot.jpg)

## Config-File
- The `config.ini` holds the following information:

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
    | targetauthheader| Base64 Representation of Username:Passwprd for authentification with the Repo (e.g. `ehrbase-user:uperSecretPassword = Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=`) |
    | targetflatapiadress | The endpoint where the FLAT-API resides (e.g. `/rest/ecis/v1/`) |
    | targetopenehrapiadress| The endpoint where the openEHR-API resides (e.g. `/rest/openehr/v1/`)|

## License
Copyright (C) 2020-2021 openehr_flat_loader contributors, see [AUTHORS.md](/AUTHORS.md)  

The openehr_flat_loader project source code is licensed under [GNU General Public License 3.0](https://spdx.org/licenses/GPL-3.0-or-later.html), see [license file](/LICENSE)  

The following third party libraries or content are part of the menoci projekt:  
* Python, Copyright © 2001-2021 Python Software Foundation, PSF License Agreement and Zero-Clause BSD license., https://docs.python.org/3/license.html
* openpyxl, Copyright (c) 2010 openpyxl, MIT Licence, https://github.com/fluidware/openpyxl/blob/master/LICENCE
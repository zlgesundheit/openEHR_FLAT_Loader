## Disclaimer

This Tool is not a finished product. Use with caution.
Only upload anonymized or pseudonymized data sets.

If you find any problems when using the program feel free to create an Issue on Gitlab.

# openEHR_FLAT_Loader

ETL-Tool to transform and upload Source Data to an openEHR-Repository (as openEHR-Resources for a given Template).  

### _Prerequisites:_
- Project was developed and tested on Windows using Python 3.8.10 with "openpyxl" and "requests"
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates (e.g. [EHRBase](https://github.com/ehrbase/ehrbase))
    - Dockered version of the EHRBase can be found from different public sources.

## Usage
1. Place some files and modify config
  - Place your .OPT-File in the Input-Folder under /OPT
  - Place your .CSV-File in the Input-Folder under /CSV
  - Edit the config.ini and at least set:
    - templatename
    - inputcsv
    - targetrepoadress  (Base adress of the openEHR-Server e.g. `http://141.5.100.199/ehrbase`)
    - targetauthheader  (Base64 encode of "username:password")
2. Run Tool using the runFlatLoader.bat on Windows (otherwise run main.py)
    - It is also possible to adjust these settings directly in the config-file 
      - -> See [Config-File](#config-file)
    - You will be asked which step of the process you want to perform
        - Step 1: Upload OPT and generate Mapping-(Excel-)File
3. To build build Compositions you have to supply mapping information in the Mapping-Table and save the Excel-file
4. Run the tool again and perform step 2:
	- Step 2: Build Compositions based on the Mapping
4. After performing Step 2 you will find the FLAT-Composition in the Output-Folder 

## Context / About openEHR
To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources a ETL-Job - for a specific Template / Operational Template - has to be built.  
The idea of [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4) as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resource using a Mapping (manually supplied by the user) from DataFields to TemplateFields.

_Process-Overview:_

![BPMN-Process-Overview](/Docs/Figures/Process_Overview_Screenshot.jpg)

## Manual (Usage and openEHR) -- Work in Progress --
A guide on how to use the tool and explaination of the context (openEHR, data curation) is currently being developed.
The manual can be found [here](/Docs/MANUAL_openEHR_FLAT_Loader.md) and is located in the "Docs" folder.

## License
Copyright (C) 2020-2021 openehr_flat_loader contributors, see [AUTHORS.md](/AUTHORS.md)  

The openehr_flat_loader project source code is licensed under [GNU General Public License 3.0](https://spdx.org/licenses/GPL-3.0-or-later.html), see [license file](/LICENSE)  

The following third party libraries or contents are part of the openEHR_FLAT_Loader projekt:  
* Python, Copyright © 2001-2021 Python Software Foundation, PSF License Agreement and Zero-Clause BSD license., https://docs.python.org/3/license.html
* openpyxl, Copyright (c) 2010 openpyxl, MIT Licence, https://github.com/fluidware/openpyxl/blob/master/LICENCE
* Pandas
* Numpy
* xlsxwriter

Part of Python Standard Libs:
* requests
* json
* configparser
* base64
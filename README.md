# openEHR_FLAT_Loader
ETL-Tool to transform Source Data and upload to an openEHR-Repository (for a given Template).

---
#### _Disclaimer_ 
This Tool is not a finished product. Put flat its a ragbag of python scripts for half-automated ETL.  
Use with caution and you may only upload anonymized or pseudonymized data sets. 


If you find any problems when using this tool feel free to create an Issue on Gitlab.

---
### _Prerequisites:_
- Project was developed and tested on Windows using Python 3.8.10 with "openpyxl" and "requests"
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates (e.g. [EHRBase](https://github.com/ehrbase/ehrbase))
    - Dockered version of the EHRBase can be found from different public sources.

---
## Usage
Features:
1. Create a Mapping-Table in xlsx/Excel-Format
2. Create Compositions and upload to openEHR-Repository
3. [PLANNED] Create an Example-Composition in FLAT or CANONICAL Json-Format

### 1. To create the Mapping-Table:

Preparation:  

    - Place your Template (.opt-File) in the Input-Folder under /OPT
    - Place your Data (.csv-File) in the Input-Folder under /CSV
    - Edit the config.ini and at least set:
        - templatename
        - inputcsv
        - targetrepoadress  (Base adress of the openEHR-Server e.g. `http://141.5.100.199/ehrbase`)
        - targetauthheader  (Base64 encode of "username:password")  

Start the Tool:  

    - Run Tool using the runFlatLoader.bat on Windows (otherwise run main.py)
        - Run Step 1 of the Tool by typing `1` and hit `Enter`

Give additional information (which the mapping requires for some Templates that include repeatable elements): 

    - If an Element in the Template can occur multiple times in one composition you will be asked how many times it occurs in your data.
        - Input the maximum number of occurences and hit enter
        - Example: Blood Pressure Value is measured multiple times per Patient
            - The Path blood_pressure:0 might hold the values about the first measurement and blood_pressure:1 the values for the second measure.

Perform and enjoy the Mapping-Task:  

    - You will find the Mapping-Table-File in Directory "ManualTasks" named by the corresponding Template
        - You can now map the `Items/Paths from the Template` to `Columns in your Data` by selecting CSV-Items from the Dropdown in Column B
        - On the Sheets "FLAT_Paths" and "CSV_Items" you find some additional information about both parts of the mapping

You might have noticed that there is some information required that is not yet included in your data

    - Mandatory data fields are marked with "Pflichtfeld" in the Mapping-Table

    - openEHR-Compositions need to hold metadata that you shall ad to your Data/.csv-File so you can map it
    - Common Metadata:
        - "<path>/composer|name": "jendrik.richter@med.uni-goettingen.de",
        - "<path>/language|code": "de",
        - "<path>/language|terminology": "ISO_639-1",
        - "<path>/territory|code": "DE",
        - "<path>/territory|terminology": "ISO_3166-1"
    - Other Metadata:
        - You can find terminologies like `openehr` online or see the Docs-Folder.
        - Example:
            Category:
            - "<path>/category|value": "event"
            - "<path>/category|code": 433
            - "<path>/category|terminology": "openehr"
            Setting:
            - "<path>/context/setting|value": "other care"
            - "<path>/context/setting|code": 238
            Any time:
            - openEHR uses ISO8601 date strings.
            - For additional information consider the [openEHR-Specification Datatypes](https://specifications.openehr.org/releases/RM/latest/data_types.html#_data_types_information_model)
        - For some fields and templates it is possible to use terminology `local` and supply any values.
        - For Questions about terminology you may contact the modellers of your specific openEHR-Template. 

    - Please note, that some elements have some metadata fields that only need to be present if the element itself is present.
        - Those are marked as "Bedingt Pflichtelement" in the Mapping-Table

    - After adding the additional metadata to the Data/.csv-File re-run step 1 of the tool.

---
### 2. To build (and upload) Resources 
    
Set Config-Variables: 

    - The config.ini-File allows you to select options 
        - `createehrs = 1` -> Tool will create EHRs in the repository 
            - This needs the names of the column(s) in the csv: `subjectidcolumn` and `subjectnamespacecolumn` or `ehrId`
            - ehrIds for these entrys will be stored in column `ehrId` in the CSV
        - `directupload = 1` -> Tool will upload the build resources for the corresponding `ehrId` in the csv
    
Start the Tool:  

    - Run Tool using the runFlatLoader.bat on Windows (otherwise run main.py)
        - Run Step 2 of the Tool by typing `2` and hit `Enter`

Enjoy the uploaded Compositions at your openEHR-Repository.

---
### 3. [PLANNED] Create an Example-Composition for a given Template
Preparation:  

    - Place your Template (.opt-File) in the Input-Folder under /OPT
    - Edit the config.ini and at least set:
        - templatename
        - targetrepoadress  (Base adress of the openEHR-Server e.g. `http://141.5.100.199/ehrbase`)
        - targetauthheader  (Base64 encode of "username:password")  

Start the Tool:  

    - Run Tool using the runFlatLoader.bat on Windows (otherwise run main.py)
        - Run Example-Creation Task of the Tool by typing `3` and hit `Enter`

Find and enjoy your Example-Composition:

    - You will find the Compositions (FLAT and Canonical) in Directory "Output" named "Example_Comp_<Template-Name>"

---
## Context / About openEHR
To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources a ETL-Job - for a specific Template / Operational Template - has to be created (most of the time this is done by by modellers / domain experts).  
The idea of [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4) as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resource using a Mapping (manually supplied by the user) from DataFields to TemplateFields.

_Process-Overview:_
![BPMN-Process-Overview](/Docs/Figures/Process_Overview_Screenshot.jpg)

---
## Manual (Usage, Example and openEHR) -- Work in Progress --
A guide on how to use the tool and explaination of the context (openEHR, data curation) is currently being developed.  
The manual can be found [here](/Docs/MANUAL_openEHR_FLAT_Loader.md) and is located in the "Docs" folder.

---
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

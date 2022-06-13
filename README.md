# openEHR_FLAT_Loader
ETL-Tool to transform Source Data into openEHR-Compositions (for a given Template) and upload those Compositions to an openEHR-Repository .

---
### Features:
1. Create a Mapping-Table in xlsx/Excel-Format
2. Create Compositions and upload those to an openEHR-Repository
3. [PLANNED] Create an Example-Composition in FLAT or CANONICAL Json-Format

---
## About openEHR and the ETL-Process
OpenEHR is a technology framework for the handling of medical data in the form of Electronic Health Records. The main point of the openEHR-Approach is the differentiation between logical modeling (in forms of archetypes/templates) and the physical storage (based on item-identifiers that are used in the technical background of these templates).

To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources an ETL-Job a specific openEHR-Template has to be created. The Template defines which data points (from which archetypes) are part of this data entry - template are later instantiated in form of resources which are send and stored by the openEHR-Server/openEHR-Repository.

The idea of the tools [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4)-Builder as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resources using a Mapping (manually supplied by the user) from DataFields to TemplateFields. With this mapping the ressources can than be generated and uploaded.

_Process-Overview:_
![BPMN-Process-Overview](/0_Docs/Figures/Process_Overview_Screenshot.jpg)

---
## Manual (Usage, Example and openEHR) **-- Work in Progress --**
A guide on how to use the tool and explanation of the context (openEHR, data curation) is currently being developed.  
For now this README describes the Import-Process in sufficient detail, the full manual can later be found [in the Docs-Folder](/Docs/MANUAL_openEHR_FLAT_Loader.md)

---
### _Prerequisites:_
Setup:
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates 
    - e.g. [EHRBase](https://github.com/ehrbase/ehrbase): A dockered version of the EHRBase can be found from different public sources.
- You may also setup a NUM Portal to manage your data and projects more easily as well as making it accessible to researcher.
    - NUM Portal offers FAIR-Search, Role-based User Management, etc.
- You need a Template (Operational Template = .opt-File) for the data you want to store.
    - e.g. download a template from a Clinical Knowledge Manager (CKM)
- You need a UTF-8 encoded CSV-File with your data.

General Procedure:
    0. Clone the FLAT-Loader
    0.1 Copy OPT and CSV to the Flat-Loader (ETLProcess/Input)
    0.2 Set correct Auth-Data and File-Names in config.ini
    1. Generate Mapping (ETProcess/ManualTasks) 
    2. Fill the Mapping (see the WebTemplate of your  for Details)
    2.1 Add missing Metadata to the CSV or in the Mapping-File
    2.2 Add Columns ehrId, id, namespace to CSV
    3. Build and Upload Compositions    
    3.1 Automated Generation of EHRs 
    3.2 Instant Upload or handle Server Feedback accordingly

- Project was developed and tested on Windows using Python 3.8.10 
- For dependencies see [License and Dependencies](#license-and-dependencies)

### Create a Mapping-Table:
0. Preparation:
    - Place your Template (.opt-File) in the Input-Folder under /OPT
    - Place your Data (.csv-File,, UTF-8 encoded) in the Input-Folder under /CSV
    - Edit the config.ini and at least set:
        - templatename (Name of your Template)
        - inputcsv (Name of your .csv-File)
        - targetrepoadress  (Base adress of the openEHR-Server e.g. `http://141.5.100.199/ehrbase`)
        - targetauthheader  (Base64 encode of "username:password")  

1. Start the Tool:  
    - Use 'run_Step1_MappingGenerator.bat' or run 'python main.py -generateMapping'

2. Follow the instructions:
    - If an Element in the Template can occur multiple times in one composition you will be asked how many times it occurs in your data.
        - Input the maximum number of occurences and hit enter
        - Example: Blood Pressure Value is measured multiple times per Patient
            - The Path blood_pressure:0 might hold the values about the first measurement and blood_pressure:1 the values for the second measure.

3. Fill out the Mapping-Table:  
    - You will find the Mapping-Table-File in Directory "ManualTasks" named by the corresponding Template
        - You can now map the `Items/Paths from the Template` to `Columns in your Data` by selecting CSV-Items from the Dropdown in Column B
        - On the Sheets "FLAT_Paths" and "CSV_Items" you find some additional information about both parts of the mapping

What to do if you need to map data fields that are not present in your source data?
    - Mandatory data fields are marked with "Pflichtfeld" in the Mapping-Table
    - openEHR-Compositions need to hold metadata that you shall add to your Data/.csv-File so you can map it
    - Common Metadata:
        - "<path>/composer|name": "jendrik.richter@med.uni-goettingen.de",
        - "<path>/language|code": "de",
        - "<path>/language|terminology": "ISO_639-1",
        - "<path>/territory|code": "DE",
        - "<path>/territory|terminology": "ISO_3166-1"
    - Other Metadata:
        - You can find terminologies like `openehr` in the Docs-Folder or online. 
            - The use of SNOMED CT and LOINC for fields with CODED_TEXTs should have been taken care of by the Template Modeller .
            - The ETLer should just be able to use the information given in the template plus some additonal openEHR-Peculiarities.
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
            Encodings:
            "<path>/encoding|code": "UTF-8",
            "<path>/encoding|terminology": "IANA_character-sets"
            - IANA character sets or the openEHR-Specification are pretty handy here -> find in Docs-Folder or online
    
    - ATTENTION! In the ManualTasks-Directory there is a file called <Template-Name>_WebTemplate.json
        - This file holds human-readable information about the structure of the Composition, it´s datatypes, CODE- and Value-Sets, Terminologies and more.
        - Search for information in the WebTemplate if you feel you are missing vital information  
          about missing metadata or data formats in the columns you have to add in your Data/.csv-File
    - For Questions about terminology you may contact the modellers of your specific openEHR-Template. 

    - Please note, that some elements have some metadata fields that only need to be present if the element itself is present.
        - Those are marked as "Bedingt Pflichtelement" in the Mapping-Table

    - After adding the additional metadata to the Data/.csv-File re-run step 1 of the tool.
        - Note that the Mapping-Table-File in ManualTasks-Directory is overwritten when re-running.
        - You may duplicate the mapping before. (The old mapping will not include newly added .csv-Columns in the Dropdowns..)

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
#### _Disclaimer_ 
This Tool is not a finished product. Use with caution and also take care of privacy needs regarding your data sets. 
If you find any problems when using this tool feel free to contact us or create an issue.

---
## License and Dependencies
Copyright (C) 2020-2021 openehr_flat_loader contributors, see [AUTHORS.md](/AUTHORS.md)  

The openehr_flat_loader project source code is licensed under [GNU General Public License 3.0](https://spdx.org/licenses/GPL-3.0-or-later.html), see [license file](/LICENSE)  

The following third party libraries or contents are part of the openEHR_FLAT_Loader projekt:  
* Python, Copyright © 2001-2021 Python Software Foundation, PSF License Agreement and Zero-Clause BSD license., https://docs.python.org/3/license.html

**Dependencies:**
* openpyxl, Copyright (c) 2010 openpyxl, MIT Licence, https://github.com/fluidware/openpyxl/blob/master/LICENCE
* Pandas / Numpy
* xlsxwriter
* requests
* chardet

**Part of Python Standard Libs:**
* json
* configparser
* base64

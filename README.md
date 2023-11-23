# openEHR_FLAT_Loader
ETL-Tool to transform Source Data into openEHR-Compositions (for a given Template) and upload those Compositions to an openEHR-Repository .

---
### Features:
1. Create an Example-Composition in FLAT JSON-Format
2. Create a Mapping-Table in xlsx/Excel-Format
3. Create Compositions and upload those to an openEHR-Repository

---
### About the Zukunftslabor Gesundheit
The [_Zukunftslabor Gesundheit_ (ZLG)](https://www.zdin.de/zukunftslabore/gesundheit) is one of the "future labs" under the umbrella organization _Zentrum für digitale Innovation Niedersachsen_ (ZDIN). 

The ZLG is a joint project of scientific institutions and local partners from the economy. In different work packages and use cases the participants push towards digitization and technological progression in health as well as translation of knowledge from researchers towards the general public.
The efforts are organized in three work groups, namely:
- TP1 - Data Infrastructure and Privacy Preserving Analysis
- TP2 - Sensors
- TP3 - Education and training

TP1 includes data management aspects, openEHR-utilization and the openEHR_FLAT_Loader.

## About openEHR and the ETL-Process
OpenEHR is a technology framework for the handling of medical data in the form of Electronic Health Records. The main point of the openEHR-Approach is the differentiation between logical modeling (in forms of archetypes/templates) and the physical storage (based on item-identifiers that are used in the technical background of these templates).

To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources an ETL-Job a specific openEHR-Template has to be created. The Template defines which data points (from which archetypes) are part of this data entry - template are later instantiated in form of resources which are send and stored by the openEHR-Server/openEHR-Repository.

The idea of the tools [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4)-Builder as well as this  **openEHR_FLAT_Loader** is to build these openEHR-Resources using a Mapping (manually supplied by the user) from DataFields to TemplateFields. With this mapping the ressources can than be generated and uploaded.

_Process-Overview:_

![BPMN-Process-Overview](/HowTo/IMG/00_etl_process_openEHR_py-svg.png)

Find an example with short explanatory README in [/HowTo/Beispieldatensatz](/HowTo/Beispieldatensatz)

---
### _Prerequisites:_
Setup:
- Check your python installation using e.g. in cmd with `python --version`. You may have to add path variables for python. In case `py --version` works, consider changing the command in the .bat-Files
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates 
    - e.g. [EHRBase](https://github.com/ehrbase/ehrbase): A dockered version of the EHRBase can be found from different public sources.
- You need a Template (Operational Template = .opt-File) for the data you want to store.
    - e.g. download a template from a Clinical Knowledge Manager (CKM)
- You need a CSV-File (we recommend ";" as delimiter) with your data.

General Procedure:  
1. Clone the FLAT-Loader-Repo  
    1.1 Copy CSV to the Flat-Loader (/ETLProcess/Input)  
    1.2 Copy OPT to OPTs-Folder (/OPTs)  
    1.3 Set correct Auth-Data and File-Names in config.ini   
2. Generate Mapping (ETProcess/ManualTasks)   
3. Fill the Mapping (see the WebTemplate of your  for Details)  
    3.1 Add missing Metadata to the CSV or in the Mapping-File  
    3.2 Add Columns ehrId, id, namespace to CSV  
4. Build and Upload Compositions      
    4.1 Automated Generation of EHRs   
    4.2 Instant Upload or handle Server Feedback accordingly  

Dependencies:
- Project was developed and tested on Windows using Python 3.8.10 
- For dependencies see [License and Dependencies](#license-and-dependencies)

---
---
## Steps in more Detail
### Create a Mapping-Table:
0. Preparation:
    - Place your Template (.opt-File) in the Input-Folder under /OPT
    - Place your Data (.csv-File,, UTF-8 encoded) in the Input-Folder under /CSV
        - a typical source-data table looks [like this](#typical-data-csv)
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

### FAQ and Hints:
##### What to do if you need to map data fields that are not present in your source data?
You will have to enrich your data with some needed metadata. About that please note:
- Mandatory data fields are marked with "Pflichtfeld" in the Mapping-Table
- Common Metadata:
    - "<path>/composer|name": "jendrik.richter@med.uni-goettingen.de",
    - "<path>/language|code": "de",
    - "<path>/language|terminology": "ISO_639-1",
    - "<path>/territory|code": "DE",
    - "<path>/territory|terminology": "ISO_3166-1"
- Other Metadata:
    - You can find terminologies like `openehr` or ISO-ValueSets online. 
    - Often you need values from LOINC or SNOMED.
    - Find local-ValueSets in the WebTemplate!
    - Examples:
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
        - IANA character sets or the openEHR-Specification are pretty handy here -> find in HowTo-Folder or online

##### I don´t have any information about the OPT. Where can i find some helpful information?
- In the ManualTasks-Directory there is a file called <Template-Name>_WebTemplate.json
    - This file holds human-readable information about the structure of the Composition, it´s datatypes, CODE- and Value-Sets, Terminologies and more.
    - Search for information in the WebTemplate if you feel you are missing vital information about missing metadata or data formats in the columns you have to add in your Data/.csv-File
- If you have access to the Clinical Knowledge Manager the OPT is coming from, you can also visit the CKM-Website and have a look at additional information about your Template.
- For Questions about terminology you may contact the modellers of your specific openEHR-Template. 

##### Why does the server reply with 400:Bad Request and indicates attribute values are missing?
- Please note, that some elements have some metadata fields that only need to be present if the element itself is present.
    - Those are marked as "Bedingt Pflichtelement" (conditionally mandatory) in the Mapping-Table
    - E.g. if you map an encoding and language for a data field, but the data field is not present for a specific patient the metadata might be present, but the attriibute/data itself is missing. In this case you may add a column that only holds encoding (code+terminology) and language (code+terminology) information **IF** the data is present for that data row/patient.

##### I did a lot of work adding mapping information, but after running step 1 again the mapping is empty!?
- After adding the additional metadata to the Data/.csv-File re-run step 1 of the tool (to have new columns in the dropdown). You may add Column Names manually, if you don´t care about having the column names in the dropdown selector.
    - Note that the Mapping-Table-File in ManualTasks-Directory is overwritten when re-running.
    - You may duplicate the mapping before. (The old mapping will not include newly added .csv-Columns in the Dropdowns..)

---
#### Typical Data CSV
The source data needs to be provided in the form of a .csv-File.

At least the file needs to contain the following columns:
- Subject Id Column (column-name specified in config.ini)
- Subject Namespace Column (column-name specified in config.ini)
- ehrId Column (which might be empty when no EHRs exist yet)

| subject-id-column | ehrId | subject_namespace | data-column1 | data-column2 | 
| ------ | ------ | ------ | ------ | ------ |
| Subject 1 |  | ExampleImport | data | data |
| Subject 2 |  | ExampleImport | data | data |
| Subject 3 |  | ExampleImport | data | data |

---
#### _Disclaimer_ 
This tool is not a finished product. Use with caution and also take care of privacy needs regarding your data sets. 
If you find any problems when using this tool feel free to contact us or create an issue.

---
## License and Dependencies
Copyright (C) 2020-2021 openehr_flat_loader contributors, see [AUTHORS.md](/AUTHORS.md)  

The openehr_flat_loader project source code is licensed under [GNU General Public License 3.0](https://spdx.org/licenses/GPL-3.0-or-later.html), see [license file](/LICENSE)  

The following third party libraries or contents are part of the openEHR_FLAT_Loader projekt:  
* Python, Copyright © 2001-2021 Python Software Foundation, PSF License Agreement and Zero-Clause BSD license., https://docs.python.org/3/license.html

**Dependencies:**
* openpyxl, Copyright (c) 2010 openpyxl, MIT Licence, https://github.com/fluidware/openpyxl/blob/master/LICENCE
* pandas
* xlsxwriter
* chardet
* requests

**Part of Python Standard Libs:**
* json
* configparser
* base64
# openEHR_FLAT_Loader
ETL-Scripts to transform Source-Data into openEHR-Compositions (for a given Template) and upload those Compositions to an openEHR-Repository.

**Using this scripts with CLI allows you to:**
1. Query an Example-Composition and WebTemplate
2. [Generate openEHR-Compositions](#steps-in-detail) from Source-Data by
    1. generating a Mapping-Table in xlsx/Excel-Format
    2. providing Mapping-Information (`CSV <> Template`)
    3. generating Compositions based on
3. [Upload generated Compositions](#to-build-and-upload-resources) to an openEHR-Repository
4. [Export/Download all Data for a specific Template](#export-all-data-of-a-template)

### About openEHR and the ETL-Process
OpenEHR is a technology framework for the handling of medical data in the form of Electronic Health Records. The main point of the openEHR-Approach is the differentiation between logical modeling (in forms of archetypes/templates) and the physical storage (based on item-identifiers that are used in the technical background of these templates).

To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources an ETL-Job a specific openEHR-Template has to be created. The Template defines which data points (from which archetypes) are part of this data entry - template are later instantiated in form of resources which are send and stored by the openEHR-Server/openEHR-Repository.

The idea of the tools [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4)-Builder as well as this  [**openEHR_FLAT_Loader**](https://github.com/zlgesundheit/openEHR_FLAT_Loader) is to build these openEHR-Resources using a Mapping (manually supplied by the user) from DataFields to TemplateFields. With this mapping the ressources can than be generated and uploaded.

#### About "clinical trial data" versus "routine or sensor data"
Please note, that the early tool development was focused on simple and structured data sets, which include a number of e.g. categorical values or some measurements like for example clinical trial data. With routine care data or sensor data the structure of the data and also the amount of data to be mapped may vary largely. Therefore the transformation and import process of the FLATLoader may not fit out of the box. 

_Data Structure Example:_
The data you have may look similar to the following bloodpressure example:  
  
![Data-Structure-Example](/HowTo/IMG/data_structure_example.png)

_Process-Overview:_

![BPMN-Process-Overview](/HowTo/IMG/00_etl_process_openEHR_py-svg.png)

Find a usage example in the HowTo-Section: [/HowTo/Beispieldatensatz](/HowTo/Beispieldatensatz)

---
### About the Zukunftslabor Gesundheit
The [_Zukunftslabor Gesundheit_ (ZLG)](https://www.zdin.de/zukunftslabore/gesundheit) is one of the "future labs" under the umbrella organization _Zentrum für digitale Innovation Niedersachsen_ (ZDIN). 

The ZLG is a joint project of scientific institutions and local partners from the economy. In different work packages and use cases the participants push towards digitization and technological progression in health as well as translation of knowledge from researchers towards the general public.
The efforts are organized in three work groups, namely:
- TP1 - Data Infrastructure and Privacy Preserving Analysis
- TP2 - Sensors
- TP3 - Education and training

TP1 includes data management aspects, openEHR-utilization and the openEHR_FLAT_Loader.

---
---
### Prerequisites:
Setup:
- Check your python installation using `python --version`. You may have to add path variables for python. In case `py --version` works, consider changing the command in the .bat-files
- You need an openEHR-Repo that supports the FLAT-Format and WebTemplates 
    - e.g. [EHRBase](https://github.com/ehrbase/ehrbase): A dockered version of the EHRBase can be found from public sources.
- You need a Template (Operational Template = .opt-File) for the data you want to store.
    - e.g. download a template from a Clinical Knowledge Manager (CKM)
- You need a CSV-File (";" as delimiter) containing your data.

General Procedure:  
1. Clone the FLAT-Loader-Repo  
    - Copy CSV to the Flat-Loader (/ETLProcess/Input)  
    - Copy OPT to OPTs-Folder (/OPTs)  
    - Set correct Auth-Data and File-Names in config.ini   
2. Generate Mapping (ETProcess/ManualTasks)   
3. Fill the Mapping (see the WebTemplate for details like cardinalities, paths, names, value-sets)  
    - Add missing Metadata to the CSV or in the Mapping-File  
    - Add columns named `ehrId`, `id`, `namespace` to CSV  (corresponding to config.ini)
4. Build and Upload Compositions      
    - Automated generation of EHRs   
    - Instant upload or handle Server Feedback accordingly  

---
## Steps in Detail
### Generate a Mapping-Table:
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
    - Use 'Step1_MappingGenerator.bat' or run 'python main.py -generateMapping'

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
### To build (and upload) Resources 
    
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
### Export all data of a Template

If you already have a repository with Templates and uploaded Compositions you can download data for a specific template as follows.

1. Set the `templatename` in config.ini
2. Run `Stepx_Export_openEHR2CSV.bat` or run main.py with `-openehr2csv`
3. The script gathers relevant paths from the WebTemplate first, then queries and stores the data in a folder `compositions_as_csvs`

---
---
## FAQ and Hints:
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
    - openEHR uses ISO8601 date strings.
    - For additional information consider the [openEHR-Specification Datatypes](https://specifications.openehr.org/releases/RM/latest/data_types.html#_data_types_information_model)
    - Examples:  
        - Category:
        ```
          - "<path>/category|value": "event"
          - "<path>/category|code": 433
          - "<path>/category|terminology": "openehr"  
        ```
        - Setting:
        ```
          - "<path>/context/setting|value": "other care"
          - "<path>/context/setting|code": 238
        ```
        - Encodings:
        ```
          - "<path>/encoding|code": "UTF-8",
          - "<path>/encoding|terminology": "IANA_character-sets"
        ```

##### I don´t have any information about the OPT. Where can i find some helpful information?
- In the ManualTasks-Directory there is a file called <Template-Name>_WebTemplate.json
    - This file holds human-readable information about the structure of the Composition, it´s datatypes, CODE- and Value-Sets, Terminologies and more.
    - Search for information in the WebTemplate if you feel you are missing vital information about missing metadata or data formats in the columns you have to add in your Data/.csv-File
- If you have access to the Clinical Knowledge Manager the OPT is coming from, you can also visit the CKM-Website and have a look at additional information about your Template.
- For Questions about terminology you may contact the modellers of your specific openEHR-Template. 

##### Why does the server reply with 400:Bad Request and indicates attribute values are missing?
- Please note, that some elements have  metadata fields that only need to be present if the element itself is present.
    - Those are marked as "Bedingt Pflichtelement" (conditionally mandatory) in the Mapping-Table
    - E.g. if you map an encoding and language for a data field, but the data field is not present for a specific patient the metadata might be present, but the attribute/data itself is missing. In this case you may alter your CSV and add a column that only holds encoding (code+terminology) and language (code+terminology) information **IF** the data is present for that data row/patient.

##### I did a lot of work adding mapping information, but after running step 1 again the mapping is empty!?
- Note that the Mapping-Table-File in ManualTasks-Directory is overwritten when re-running.
  - You may duplicate the mapping before re-running. (The old mapping will not include newly added .csv-Columns in the Dropdowns..)
    - You may manually add Column-Names to the mapping file, if you don´t care about having the column names in the dropdown selector.
    - After adding  additional metadata to the Data/.csv-File re-run step 1 of the tool to have new columns in the dropdown. 

---
#### Typical Data CSV
The source data needs to be provided in the form of a .csv-File.

Best works `UTF-8` encoding with `;` as separator.

At least the file needs to contain the following columns:
- Subject-Id-Column (column-name specified in config.ini)
- Subject-Namespace-Column (column-name specified in config.ini)
- ehrId-Column (often empty when no EHRs exist yet)

| subject-id-column | ehrId | subject_namespace | data-column1 | data-column2 | 
| ------ | ------ | ------ | ------ | ------ |
| Subject 1 |  | ExampleImport | data | data |
| Subject 2 |  | ExampleImport | data | data |
| Subject 3 |  | ExampleImport | data | data |

---
#### _Disclaimer_ 
This tool is not a finished product. Use with caution and also take care of privacy needs regarding your data sets. 
If you find any problems when using this tool feel free to contact us.

---
## License and Dependencies
Copyright (C) 2020-2021 openehr_flat_loader contributors, see [AUTHORS.md](/AUTHORS.md)  

The openehr_flat_loader project source code is licensed under [GNU General Public License 3.0](https://spdx.org/licenses/GPL-3.0-or-later.html), see [license file](/LICENSE)  

The following third party libraries or contents are part of the openEHR_FLAT_Loader project:  
* Python, Copyright © 2001-2021 Python Software Foundation, PSF License Agreement and Zero-Clause BSD license., https://docs.python.org/3/license.html

**Dependencies:**
* openpyxl
* pandas
* xlsxwriter
* chardet
* requests

# MANUAL_openEHR_FLAT_Loader

`Zukunftslabor Gesundheit`  
`Jendrik Richter (UMG), Jan Janosch Schneider (UMG)`

`COFONI`  
`Mareike Joseph (MHH)`

`Kontakt:`  
`jendrik.richter@med.uni-goettingen.de`

`08/2021`

## Contents
[[_TOC_]]

## Updates
#### xx/2021
- Release of Version 1.0

## Introduction
This manual describes how the **openEHR_FLAT_Loader** can be used to transform tabular data into openEHR-Resources / openEHR-Compositions.  
  
The **openEHR_FLAT_Loader** is a joint development by researchers from these projects:
- _Zukunftslabor Gesundheit (ZL-G)_, 
- _Covid-19 Forschungsnetzwerk Niedersachsen (COFONI)_ 
- _A Learning and Interoperable Smart Expert System for Pediatric Intensive Care Medicine (ELISE)_

The above mentioned projects needed researchers and end user to be able to generate valid openEHR-Resources from existing non-openEHR data.
The **[HaMSTR-Builder-Tool](https://gitlab.plri.de/tute/HAMSTRETLBuilder)** developed by the _Hannover Medical School (MHH)_ already offered this functionality but needed a (commercial) Better / thinkEHR openEHR-Repository to work. The present FLAT_Loader tool, similar to the HaMSTR builder, builds on the idea of a user-supplied mapping. The **openEHR_FLAT_Loader** allows the user to generate resources using a mapping from data-items to openEHR-Template items. The openEHR-Template items are derived directly from Webtemplates for given Operational Templates.

Webtemplates are part of the FLAT-API as it is used in Better, EHRBase and EtherCIS openEHR-Servers.
In the future this will be adopted into the openEHR-Standard as a so called [Simplified Data Template (simSDT)](https://specifications.openehr.org/releases/ITS-REST/latest/simplified_data_template.html).
We hope to stay (or become) compatible with the standard in the future.

#### Requirements
- openEHR-Server supporting the FLAT-API (e.g. EHRBase)
- Python 3.8 with modules "openpyxl" and "requests"

## Features
- Extraction of FLAT-Paths 
  - from Webtemplates
- Tips and Hints for Data Curation 
  - regarding the planned transformation
- Generation of a Mapping-File 
  - Excel-File (.xlsx)
- Build Ressources 
  - using a provided .csv, .opt and filled Mapping-File
- Upload Ressources 
  - using identifier-column .csv-data-file 

## Data Modeling / Template Creation
Templates (and Archetypes) are created by domain experts either by selecting existing archetypes (which represented specific clinical concepts) or creating new archetypes in collaboration with the (openEHR-) Community. 

TODO: Hinweise zur Modellierung --> Darstellen wie Templates zustande kommen --> Siehe unten Template

#### Data Modelling (openEHR)
- **openEHR-Specification**  
The [specification of openEHR](https://specifications.openehr.org) holds nearly ALL important information about openEHR.
This information is best used accompanied by information from [community discussions](https://discourse.openehr.org), examples and available open-source openEHR-Servers (e.g. [EHRBase](https://github.com/ehrbase/ehrbase)).

- **Information Model / Reference Model**  
The openEHR [information model](https://specifications.openehr.org/releases/RM/latest/ehr.html) describes how data is structured in the openEHR-World. Data is organized in EHRs (so it is patient-centered) holding information about the EHR(Access, Status) and the EHR that may contain folders / directorys which contain the compositions that hold the data, in form of defined data types and attributes taken from the Reference Model. The structure of compositions that hold the data is defined by Templates (that use Archetypes, which are the Core of openEHR)

  <img src="/Docs/Figures/openEHR_Information_Model_High_Level_Structure.jpg">

- **Archetypes**  
[OpenEHR-Archetypes](https://specifications.openehr.org/releases/AM/latest/Overview.html) are defined in Archetype Definition Language (ADL). In the multi-level-modelling approach of openEHR they allow to distinct between domain semantics and the information model / reference model. An Archetype is a reusable definition of a semantic concept from a domain, which correspond to logical data points and groups. Archetypes / Semantic concepts should be designed and maintained by domain experts. Often the archetype and template development takes place in [Clinical Knowledge Managers (CKM)](https://ckm.openehr.org/ckm/).

  <img src="/Docs/Figures/openehr_archetype_figure.jpg">

- **Templates**  
An openEHR-Template defines an arrangement of items from one or more archetypes, possibly with further constraints on them (regarding cardinality, inputs, etc.). A Template defines how a composition of data looks like and is used at runtime to create data structures and validate inputs.

- **Webtemplates and FLAT-Paths**  
A Webtemplate is an other format of a Template (Operational Template / .opt). Webtemplates are Part of the [FLAT-API](https://ehrbase.readthedocs.io/en/latest/02_getting_started/05_load_data/index.html) at first used by EtherCIS and Better and later EHRBase. The FLAT-API allows to communicate with the server using Compositions in FLAT-Format, which means they are structured a non-hierarchical JSON-Strings using FLAT-Paths to define which data item is assigned which value. This format is easy to read, understand and easy to work with.

  <img src="/Docs/Figures/FLAT_Composition_Example.jpg">

## Data Preparation
There are some noteworthy aspects in preparing the data to be consumed by the FLAT_Loader. Aligning **data types** and **item/column names** and **some metadata** with the **data model / openEHR-Template** makes the transformation process easy.

#### Data Curation
Curate your data and make sure to only generate (and upload) data with high data quality that matches your needs and the needs of others working with the data in the future.

#### Formatting
The data formatting has to comply on one hand with constraints in the data model (e.g. Date and Time formatting according to standards defined in openEHR) and on the other hand with constraints of the FLAT_Loader (e.g. Id-Column name, metadata like language, status codes and encoding info to build valid resources). 

How to format the data will be explained in the following:
TODO

#### Identificators/Pseudonymisation

## Tool Usage Steps
``Work in progress`

0. Place your .OPT-File in the Input-Folder
1. Run Tool using the runFlatLoader_win.bat on Windows or runFlatLoader_lin.sh if you are on Linux.
   If you use a MAC try starting the runMain.py in Scripts-Directory...
    - If the config-file is not existing you will be asked to provide some config-settings. 
    - It is also possible to adjust these settings directly in the config-file 
      - -> See [Config-File](#config-file)
    - You will be asked which step of the process you want to perform
        - Step 1: Upload OPT and generate Mapping-(Excel-)File
2. To build build Compositions you have to supply mapping information in the Mapping-Table and save the Excel-file
3. Run the tool again and perform step 2:
	- Step 2: Build Compositions based on the Mapping
4. After performing Step 2 you will find the FLAT-Composition in the Output-Folder 
5. Automated upload is not yet implemented

#### 0.1 Provide data as .csv
After Data Preparation, Curation and Formatting 
- Move the CSV-File to "<pathToTool>\openehr_flat_loader\Input\CSV\"
- Set the InputCSV-File that will be dealed with by the tool
  - Change the "inputcsv"-Variable in the config to the current CSV-Filename
  - See Step "0.3 Set config.ini-Values"

#### 0.2 Provide a template as .opt
- Get the Operational Template for your Data Set 
  - E.g. download the OPT-File (.opt) from a Clinical Knowledge Manager (CKM) using the Export-Functionality  
    <img src="/Docs/Figures/ckm_template_mark.jpg">
- Move the OPT-File to "<pathToTool>\openehr_flat_loader\Input\OPT\"
- Set the Template that will be dealed with by the tool
  - Change the "templatename"-Variable in the config to the current Templatename
  - See Step "0.3 Set config.ini-Values"

#### 0.3 Set config.ini-Values
- Set Workdir to the directory in which you have placed the "openehr_flat_loader"-Tool
- Set templatename and inputcsv according to the names of the files the tool shall deal with
- Set information about the openEHR-Repository you want to upload to (Adress,Auth,API-Adresses)
- The `config.ini` holds the following information:
    **Environment Infos:**
    | config-variable | Description |
    | --------------- | ------ |
    | workdir         | Working Directory (e.g. `C:\Users\richter\git-projects\openehr_flat_loader`) |
    | templatename    | Name of the Template (e.g. `UMG_Stammdaten`) |
    | inputcsv        | Name of the csv-file that holds the data (`source_data`) |
    
    **Repository Infos:**
    | config-variable | Description |
    | --------------- | ------ |
    | targetrepoadress| Baseadress of the Target Repo (e.g. `http://141.5.100.199/ehrbase`) |
    | targetauthheader| Base64 Representation of Username:Password for authentification with the Repo (e.g. `ehrbase-user:uperSecretPassword = Basic ZWhyYmFzZS11c2VyOlN1cGVyU2VjcmV0UGFzc3dvcmQ=`) |
    | targetflatapiadress | The endpoint where the FLAT-API resides (e.g. `/rest/ecis/v1/`) |
    | targetopenehrapiadress| The endpoint where the openEHR-API resides (e.g. `/rest/openehr/v1/`)|

#### 1. Generate an empty mapping file
- Start the tool using "runFlatLoader_win.bat"
- Select Step 1 by typing "1" + press "Enter"

  <img src="/Docs/Figures/cmd_step1.jpg">

#### 2. Fill in mapping information
- Find the (empty) mapping file in "openehr_flat_loader\Manual Tasks\" by looking for <<templatename>>_MAPPING.xlsx
- Select CSV-Items from the Dropdown and map them to FLAT-Paths from the Template

  <img src="/Docs/Figures/mapping_file.jpg">

#### 3. Build Ressources
- Start the tool using "runFlatLoader_win.bat"
- Select Step 2 by typing "2" + press "Enter"

  <img src="/Docs/Figures/cmd_step1.jpg">

`Resources can be found in "openehr_flat_loader\Output\"`

#### 4. Upload Ressources

## Funding
- Funded by the Lower Saxony Ministry of Science and within the Lower Saxony “Vorab“ of the Volkswagen Foundation and supported by the Center for Digital Innovations (ZDIN).
- Funds of the participating institutes

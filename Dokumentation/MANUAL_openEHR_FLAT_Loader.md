# MANUAL_openEHR_FLAT_Loader

`Zukunftslabor Gesundheit`  
`Jendrik Richter (UMG), Jan Janosch Schneider (UMG), Mareike Joseph (MHH)`

`jendrik.richter@med.uni-goettingen.de`

`08/2021`

## Contents
- [Updates](#updates)
- [Introduction](#introduction)
  - [Requirements](#requirements)
- [Features](#features)
- [Data Preparation](#data-preparation)
  - [Data Curation](#data-curation)
  - [Formatting](#formatting)
  - [Data Modelling (openEHR)](#data-modelling-(openehr))
  - [Identificators/Pseudonymisation](#identificators/pseudonymisation)
- [Tool Usage Steps](#Tool-Usage-Steps)
  - [0. Provide data as .csv](#0-provide-data-as-.csv)
  - [0. Provide a template as .opt](#0-provide-a-template-as-.opt)
  - [0. Set config.ini-Values](#0-set-config-ini-values)
  - [1. Generate an empty mapping file](#1-generate-an-empty-mapping-file)
  - [2. Fill in mapping information](#2-fill-in-mapping-information)
  - [3. Build Ressources](#3-build-ressources)
  - [4. Upload Ressources](#4-upload-ressources)
- [Funding](#funding)

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
In the future this will be adopted into the openEHR-Standard as a so called [Simplified Data Format](https://specifications.openehr.org/releases/ITS-REST/latest/simplified_data_template.html).
We hope to stay (or become) compatible with the standard in the future.

#### Requirements
- openEHR-Server supporting the FLAT-API (e.g. EHRBase)
- Python 3.8 with modules "openpyxl" and "requests"

## Features

## Data Preparation

#### Data Curation
#### Formatting
#### Data Modelling (openEHR)
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

#### 0. Provide data as .csv
#### 0. Provide a template as .opt
#### 0. Set config.ini-Values
#### 1. Generate an empty mapping file
#### 2. Fill in mapping information
#### 3. Build Ressources
#### 4. Upload Ressources

## Funding
- Funded by the Lower Saxony Ministry of Science and within the Lower Saxony “Vorab“ of the Volkswagen Foundation and supported by the Center for Digital Innovations (ZDIN).
- Funds of the participating institutes

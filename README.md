# openEHR_FLAT_Loader

ETL-Tool to transform Source Data into openEHR-Resources.  

## Context
To transform data from different sources (e.g. SQL-DB, CSV, etc.) into openEHR-Resources a ETL-Job - for a specific Template / Operational Template - has to be built.
The idea of [**HaMSTR**](https://gitlab.plri.de/tute/HAMSTRETLBuilder/-/tree/a58c9f479ab9d5f6ebad10906963949a806ad7c4) as well as this **openEHR_FLAT_Loader** is to build these openEHR-Resource using a Mapping (manuall supplied by the user) from DataFields to TemplateFields.


## Work in Progress:
- Fix the MappingDetection of the CompositionBuilder
- Dealing with multiple Index-Entrys in FLAT-Paths (for the start just support up to 3)
- GUI with good Usability
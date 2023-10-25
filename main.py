#########################################################################
# ETL-Pipeline from CSV to openEHR-Compositions
# 
# 1. Upload Template and get WebTemplate
# 2. Generate Mapping List from WebTemplate
# 3. (Manual Task) Mapping-List ausfüllen
# 4. Build Compositions
#
# Developed and tested with Python 3.8.10 (+ 3.10.4)
#
# Jendrik Richter (UMG)
#########################################################################
# Standard library imports
import os.path
from os import getcwd
import sys
import traceback
# Third party imports
# Local application/script imports
from Scripts import handleConfig
from Scripts import handleOPT
from Scripts import buildComp
from Scripts import handleWebTemplate
from Scripts import buildMapping
from Scripts import handleUpload
from Scripts import queryExampleComp
from Scripts import aqlBuilder
from Scripts import csv_export

#Init Config-Object
config = handleConfig.config()
indent = "\t"
workdir = getcwd()

# TODO Set all Paths here or in configHandler? centralized and pass them to the other scripts. SinglePointOfChange
OPTDirPath      = os.path.join(workdir, 'OPTs')
sourceDataCsvFP = os.path.join(workdir, 'ETLProcess','Input', config.inputCSV + '.csv')
manualTaskDir   = os.path.join(workdir, 'ETLProcess', 'ManualTasks', config.templateName)
outputDir       = os.path.join(workdir, 'ETLProcess', 'Output', config.templateName)

############################### Main ###############################
def main():
    """Takes start parameter from command line call. Runs selected scripts for selected feature."""
    global guessed_encoding

    # Check if all directories exist otherwise create them
    dir_exists()

    # Run Scripts for the argument that was passed
    if (len(sys.argv) <= 1):
        print("Use arguments '-setup_new_template, -generateMapping', '-buildAndUploadCompositions' or '-openehr2csv'.")
        raise SystemExit
    else:
        print("Used Argument: " + sys.argv[1])

    # Argument: -generateMapping
    if (sys.argv[1] == '-generateMapping'):
        # Show Explanatory Text on how to use the tool and what steps to perform to the User
        print_welcome_text()
        generate_mapping()
    # Argument: -buildAndUploadCompositions
    elif (sys.argv[1] == '-buildAndUploadCompositions'):
        # Show Explanatory Text on how to use the tool and what steps to perform to the User
        print_welcome_text()
        build_and_upload_compositions()
    # Argument: -setup_new_template
    elif (sys.argv[1] == '-setup_new_template'):
        setup_new_template()
    # Argument: openehr2csv
    elif (sys.argv[1] == '-openehr2csv'):
        export_openehr2csv()
    # Terminate

############################### Methods ###############################
def generate_mapping():
    """Queries WebTemplate and extracts Path-Values to create Excel-Mapping-File."""

    # Upload OPT to openEHR-Repo if necessary
    webTemp = handleOPT.main(config,manualTaskDir,OPTDirPath)

    # Extrahiere Pfade in Array von Pfadobjekten 
    pathArray = handleWebTemplate.main(webTemp, config.templateName)

    csv_dataframe = handleConfig.read_csv_as_df(config.inputCSV)

    # Baue Mapping
    buildMapping.main(manualTaskDir,config.templateName, csv_dataframe, pathArray, allindexesareone = config.allindexesareone)

def build_and_upload_compositions():
    """Generates compositions using CSV-Data and supplied Mapping-Information from Excel-File. 
       If activated in config those are uploaded to the specified directory. """
    resArray = buildComp.main(config,manualTaskDir,outputDir)

    # Create EHRs for all patients in csv
    if config.createehrs == "1":  # EHRCreation could be an extra-parameter
        csv_dataframe = csv_dataframe = handleConfig.read_csv_as_df(config.inputCSV)
        anzahl_eintraege = len(csv_dataframe.index)

        # Check for existence of columns: ehrId, namespace-column from config, subjectID-column from config -> else error-message and systemexit
        if not ('ehrId' in csv_dataframe.columns and config.subjectidcolumn in csv_dataframe.columns and config.subjectnamespacecolumn in csv_dataframe.columns):
            print ("The Input-Data needs to contain columns for 'ehrId' as well as the ID-Column ["+ config.subjectidcolumn +"] and Namespace-Column ["+ config.subjectnamespacecolumn +"] defined in config.ini")
            raise SystemExit

        print (f'Create {anzahl_eintraege} EHRs:')
        ehr_counter = 0
        csv_dataframe, ehr_counter = handleUpload.create_all_ehr(config.targetAdress, config.targetAuthHeader, csv_dataframe, config.subjectidcolumn , config.subjectnamespacecolumn, ehr_counter)
        print ("EHRs for " + str(ehr_counter) + " / " + str(anzahl_eintraege) + " Subjects have been created successfully.\n")
        csvPath = sourceDataCsvFP
        csv_dataframe.to_csv(csvPath, sep=";", index = False, encoding = "UTF-8")
    else:
        print ("EHR Creation is disabled in Config.ini")
        pass

    # Send resource to server
    if config.directupload == "1":
        csv_dataframe = handleConfig.read_csv_as_df(config.inputCSV)
        anzahl_eintraege = len(csv_dataframe.index)

        print ("Upload "+ str(anzahl_eintraege) +" Compositions:")
        quick_and_dirty_index = 0
        comp_created_count = 0
        for res in resArray:
            # Wird dann in buildComp auffgerufen, liest hier die aktuelle CSV mit ehrIds ein
            ehrId = csv_dataframe['ehrId'][quick_and_dirty_index]
            compositionUid, comp_created_count = handleUpload.upload_comp_to_ehrid(config.targetAdress, config.targetAuthHeader, ehrId, res, config.templateName, comp_created_count)
            quick_and_dirty_index += 1

        print (str(comp_created_count) + " / " + str(anzahl_eintraege) + " Compositions have been created successfully.\n" )    
        print ("Upload finished. Great Success.")
    else:
        print ("Direct Upload is disabled in Config.ini")
        pass
    
def export_openehr2csv():
    """Generates and runs an AQL-Query to export all data of a specific Template into a CSV-File."""
    csv_export.main(config,manualTaskDir)

def setup_new_template():
    """Queries example composition from FLAT-API example endpoint of ehrbase. TODO Also query Better Example Endpoint. Idenntify which is present.
    {{host}}/rest/ecis/v1/template/:template_id/example?format=FLAT

    Args:
        None

    Returns:
        None

    """

    print(f"Upload OPT {config.templateName} and download WebTemplate + Example-Composition")

    # Upload OPT to openEHR-Repo if necessary
    webTemp = handleOPT.main(config,manualTaskDir,OPTDirPath)

    # Query Example Comp 
    exampleComp = queryExampleComp.query_example_composition(config.templateName, config.targetAdress, config.targetAuthHeader)
    # Store example comp in ManualTaskFolder
    queryExampleComp.store_string_as_file(exampleComp, manualTaskDir, config.templateName + "CompositionExample" + ".json")
    # Store Webtemplate in Example-Folder
    queryExampleComp.store_string_as_file(webTemp, manualTaskDir, config.templateName + "_WebTemplate" + ".json")

    print("\nOPT is uploaded to the Repository and an Example-Composition is stored in the ManualTasks-Folder.")
    print("\nDone.")

def print_welcome_text():
    """Prints CLI 'Welcome'-Message and short explanation of what the Tool/Scripts do."""
    print("    Welcome to the openEHR_FLAT_Loader-Commandline-Tool!")
    print("    Given an existing template, this tool allows you to transform tabular data into the interoperable openEHR format."
        + "       Variables for template, data/csv-file and repository can be specified in config.ini."
    )

def dir_exists():
    """ """
    if not os.path.isdir(manualTaskDir):
        create_dir(manualTaskDir)

    if not os.path.isdir(outputDir):
        create_dir(outputDir)

def create_dir(path):
    """

    Args:
      path:

    Returns:

    Raises:
        OSError: Error with creating the folder.
    """
    access_rights = 0o755
    try:
        os.mkdir(path, access_rights)
    except OSError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        print ("Creation of the directory %s failed" % path)
        raise SystemExit
    else:
        print ("Successfully created the directory %s" % path)

if __name__ == '__main__':
    main()
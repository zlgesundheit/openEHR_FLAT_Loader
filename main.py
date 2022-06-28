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
from Scripts import buildExampleComp

#Init Config-Object
config = handleConfig.config()
indent = "\t"
workdir = getcwd()
sourceDataCsvFP = os.path.join(workdir, 'ETLProcess', 'Input', config.inputCSV + '.csv')
OPTDirPath      = os.path.join(workdir, 'OPTs')
manualTaskDir   = os.path.join(workdir, 'ETLProcess', 'ManualTasks', config.templateName)
outputDir       = os.path.join(workdir, 'ETLProcess', 'Output', config.templateName)
# TODO Set all Paths here or in configHandler? centralized and pass them to the other scripts. SinglePointOfChange

############################### Main ###############################
def main():
    global guessed_encoding

    # Check if all directories exist otherwise create them
    checkIfDirsExists()

    # Run Scripts for the argument that was passed
    if (len(sys.argv) <= 1):
        print("Use arguments '-generateMapping', '-buildAndUploadCompositions' or '-generateExamples'.")
        raise SystemExit
    else:
        print("Used Argument: " + sys.argv[1])

    # Argument: -generateMapping
    if (sys.argv[1] == '-generateMapping'):
        # Show Explanatory Text on how to use the tool and what steps to perform to the User
        printInfoText()
        generateMapping()
    # Argument: -buildAndUploadCompositions
    elif (sys.argv[1] == '-buildAndUploadCompositions'):
        # Show Explanatory Text on how to use the tool and what steps to perform to the User
        printInfoText()
        buildAndUploadCompositions()
    # Argument: -generateExamples
    elif (sys.argv[1] == '-generateExamples'):
        generateExamples()
    # Terminate

############################### Methods ###############################
def generateMapping():
    # Upload OPT to openEHR-Repo if necessary
    webTemp = handleOPT.main(config,manualTaskDir,OPTDirPath)

    # Extrahiere Pfade in Array von Pfadobjekten 
    pathArray = handleWebTemplate.main(webTemp, config.templateName)

    csv_dataframe = handleConfig.readCSVasDataFrame(config.inputCSV)

    # Baue Mapping
    buildMapping.main(manualTaskDir,config.templateName, csv_dataframe, pathArray, allindexesareone = config.allindexesareone)

def buildAndUploadCompositions():
    resArray = buildComp.main(config,manualTaskDir,outputDir)

    # Create EHRs for all patients in csv
    if config.createehrs == "1":  # EHRCreation could be an extra-parameter
        csv_dataframe = csv_dataframe = handleConfig.readCSVasDataFrame(config.inputCSV)
        anzahl_eintraege = len(csv_dataframe.index)

        # Check for existence of columns: ehrId, namespace-column from config, subjectID-column from config -> else error-message and systemexit
        if not ('ehrId' in csv_dataframe.columns and config.subjectidcolumn in csv_dataframe.columns and config.subjectnamespacecolumn in csv_dataframe.columns):
            print ("The Input-Data needs to contain columns for 'ehrId' as well as the ID-Column ["+ config.subjectidcolumn +"] and Namespace-Column ["+ config.subjectnamespacecolumn +"] defined in config.ini")
            raise SystemExit

        print (f'Create {anzahl_eintraege} EHRs:')
        ehr_counter = 0
        csv_dataframe, ehr_counter = handleUpload.createEHRsForAllPatients(config.targetAdress, config.targetAuthHeader, csv_dataframe, config.subjectidcolumn , config.subjectnamespacecolumn, ehr_counter)
        print ("EHRs for " + str(ehr_counter) + " / " + str(anzahl_eintraege) + " Subjects have been created successfully.\n")
        csvPath = sourceDataCsvFP
        csv_dataframe.to_csv(csvPath, sep=";", index = False, encoding = "UTF-8")
    else:
        print ("EHR Creation is disabled in Config.ini")
        pass

    # Send resource to server
    if config.directupload == "1":
        csv_dataframe = handleConfig.readCSVasDataFrame(config.inputCSV)
        anzahl_eintraege = len(csv_dataframe.index)

        print ("Upload "+ str(anzahl_eintraege) +" Compositions:")
        quick_and_dirty_index = 0
        comp_created_count = 0
        for res in resArray:
            # Wird dann in buildComp auffgerufen, liest hier die aktuelle CSV mit ehrIds ein
            ehrId = csv_dataframe['ehrId'][quick_and_dirty_index]
            compositionUid, comp_created_count = handleUpload.uploadResourceToEhrId(config.targetAdress, config.targetAuthHeader, ehrId, res, config.templateName, comp_created_count)
            quick_and_dirty_index += 1

        print (str(comp_created_count) + " / " + str(anzahl_eintraege) + " Compositions have been created successfully.\n" )    
        print ("Upload finished. Great Success.")
    else:
        print ("Direct Upload is disabled in Config.ini")
        pass
    
def generateExamples():
    """ Beispiele werden generiert, wenn die Pfade aus dem WebTemplate ausgelesen werden. Zu jedem Pfad wird abhängig vom Datentyp/rmType ein Beispielwert erzeugt.
    Danach kann also zu jedem Pfad im Pfad-Dict nicht nur der Pfad (pathString) sondern auch Beispiele abgerufen werden (exampleValueDict). 
    
    Implementierung fast aller rmTypes mit Beispielen hat beim Verständnis des der Strukturen des Webtemplates sehr geholfen.
    Inzwischen bietet die FLAT-API der EHRBase allerdings einen Example-Endpunkt:
    {{host}}/rest/ecis/v1/template/:template_id/example?format=FLAT

    """

    # Upload OPT to openEHR-Repo if necessary
    webTemp = handleOPT.main(config,manualTaskDir,OPTDirPath)

    # Query Example and store in 
    exampleComp = buildExampleComp.queryExampleComp(workdir, config.templateName, config.targetAdress, config.targetAuthHeader)
    buildExampleComp.storeStringAsFile(exampleComp, manualTaskDir, config.templateName + "CompositionExample" + ".json")

    # Store Webtemplate in Example-Folder
    buildExampleComp.storeStringAsFile(webTemp, manualTaskDir, config.templateName + "_WebTemplate" + ".json")

    print("\n")
    print("OPT is uploaded to the Repository and an Example-Composition is stored in the ManualTasks-Folder.")

    """
    # Extrahiere Pfade in Array von Pfadobjekten 
    pathArray = handleWebTemplate.main(webTemp, config.templateName)

    # Build Minimal Example
    buildExampleComp.main(workdir, pathArray, config.templateName, config.targetAdress, config.targetAuthHeader, "min")
    # Build Maximal Example
    buildExampleComp.main(workdir, pathArray, config.templateName, config.targetAdress, config.targetAuthHeader, "max")
    """
def printInfoText():
    print("    Welcome to the openEHR_FLAT_Loader-Commandline-Tool!")
    print("    Given an existing template, this tool allows you to transform tabular data into the interoperable openEHR format."
        + "       Variables for template, data/csv-file and repository can be specified in config.ini."
    )

def checkIfDirsExists():
    if not os.path.isdir(manualTaskDir):
        createDir(manualTaskDir)

    if not os.path.isdir(outputDir):
        createDir(outputDir)

def createDir(path):
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
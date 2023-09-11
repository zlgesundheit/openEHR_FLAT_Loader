from Scripts import handleConfig, handleOPT, handleWebTemplate
import os
import re
import requests
import util

#os.chdir("..")
workdir = os.getcwd()

config = handleConfig.config()
OPTDirPath      = os.path.join(workdir, 'OPTs')
manualTaskDir   = os.path.join(workdir, 'ETLProcess', 'ManualTasks', config.templateName)
print(config.templateName)

webTemp = handleOPT.main(config,manualTaskDir,OPTDirPath)

# Extrahiere Pfade in Array von Pfadobjekten
elements = handleWebTemplate.main(webTemp, config.templateName)[1]

aql_path_values = [d["aqlPath"] for d in elements]

def remove_and_statements(input_string):
    # Regex-Pattern zum Ersetzen von " and ..." durch "]"
    pattern = r' and [^\]]*\''
    adjusted_string = re.sub(pattern, "",input_string)
    return adjusted_string


def generate_aql(aql_path_values):
    assert len(aql_path_values) > 0, "The webtemplate does not contain any aql paths"
    aql_string = "SELECT "

    for index, value in enumerate(aql_path_values):
        if index == len(aql_path_values) - 1:
            aql_string += "c" + value
        else:
            aql_string += "c" + value + ", "

    aql_string = aql_string + " FROM EHR e contains COMPOSITION c"
    adjusted_aql_string = remove_and_statements(aql_string)
    aql_dict = {"q": adjusted_aql_string}

    return adjusted_aql_string

adjusted_aql_string = generate_aql(aql_path_values)
resp = util.sendAqlRequest(config.targetAdress, config.targetAuthHeader, "9999999999999", adjusted_aql_string)
util.storeRespAsCSV(workdir, "compositions_as_csvs", resp, config.templateName+".csv")



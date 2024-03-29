# Context: Use Case Cardiology from HiGHmed
# Environment: Better Repo (Only relevant for AQL-Syntax)
#
# Developed and tested with Python 3.10.4
#
# Lennart Graf (UMG)
#########################################################################

import os
from Scripts import handleOPT, handleWebTemplate, handleConfig
from Scripts import util

def main(config):
    """

    Args:
      config: param manualTaskDir:
      manualTaskDir: 

    Returns:

    """
    workdir = os.getcwd()
    template_from_config = input("Select the given template from config (y/n)?")
    template_list = util.get_templates_from_server(config)
    if template_from_config != "y":
        manual_template_from_cli(config, template_list)
        config = handleConfig.config()

    assert input_in_template_list(config.templateName, template_list), ("The input didn't match any of the given "
                                                                         "templates. Please try again and select one of "
                                                                        "templates from the list.")
    manual_task_dir =  util.create_manueal_task_dir(workdir, config.templateName)
    webTemp = handleOPT.get_webtemplate(config, manual_task_dir)

    # Extrahiere Pfade in Array von Pfadobjekten
    web_temp_elmnts = handleWebTemplate.main(webTemp, config.templateName)

    aql_path_values = [d.aql_path for d in web_temp_elmnts]


    adjusted_aql_string = generate_aql(aql_path_values)
    resp = util.send_aql_request(config.targetAdress, config.targetAuthHeader, "9999999999999", adjusted_aql_string)
    util.store_resp_as_csv(workdir, "compositions_as_csvs", resp, config.templateName+".csv", web_temp_elmnts)
def manual_template_from_cli(config, template_list):
    print("Please select one of the given templates to which you want to have all compositions from the server.")

    print_all_templates(template_list)
    template_name = input("Template: ")
    handleConfig.set_template_name(template_name)
def generate_aql(aql_path_values):
    """

    Args:
      aql_path_values: 

    Returns:

    """
    assert len(aql_path_values) > 0, "The webtemplate does not contain any aql paths"
    aql_string = "SELECT "

    for index, value in enumerate(aql_path_values):
        if index == len(aql_path_values) - 1:
            aql_string += "c" + value
        else:
            aql_string += "c" + value + ", "

    aql_string = aql_string + " FROM EHR e contains COMPOSITION c"
    adjusted_aql_string = util.remove_and_statements(aql_string)

    return adjusted_aql_string

def print_all_templates(all_templates: list) -> None:
    """Prints each entry of a list of templates in the cli, so that each entry is on a single line.

    Args:
      all_templates: list:
      all_templates: list:
      all_templates: list: 

    Returns:

    """
    for template in all_templates:
        print(template)

def input_in_template_list(input, template_list):
    if input in template_list:
        return True
    else:
        return False

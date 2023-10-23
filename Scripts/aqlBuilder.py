import os
from Scripts import handleConfig, handleOPT, handleWebTemplate
import requests
from Scripts import util

def main(config,manualTaskDir):
    #os.chdir("..")
    workdir = os.getcwd()

    #config = handleConfig.config()
    #OPTDirPath      = os.path.join(workdir, 'OPTs')
    #manualTaskDir   = os.path.join(workdir, 'ETLProcess', 'ManualTasks', config.templateName)
    print(config.templateName)

    ### User muss Template-Namen angeben (in Config oder TODO lieber abfragen)
    ### TODO User startet Step_x.bat  (Vorher in config: serveradresse + authinfo)
    ### TODO Dann: Vom angegebenen Server werden alle Templates abgefragt und der Nutzer 
    ### kann aus einer Liste auswählen zu welchem template er Daten abfragen will.
    ### Eingabe in config speichern oder direkt verwenden
    webTemp = handleOPT.get_webtemplate(config,manualTaskDir)

    # Extrahiere Pfade in Array von Pfadobjekten
    web_temp_elmnts = handleWebTemplate.main(webTemp, config.templateName) # TODO: return of andleWebTemplate.main() is array, little bit ugly

    ### TODO Muss man das nochmal anfassen
    ### TODO Hier könnten die bestehenden pfadobjekte um ein "aqlPfad" attribut erweitert werden -> erledigt
    ### -> das müsste IN der handlewebtemplate entsprechend beim auslesen hinzugefügt werden -> erledigt
    ### Das hieße, dass man auch nur die AQL-Pfade hat, von Elementen wo Daten drin stehen, z.B. nicht von CLustern, o.ä.
    ### TODO Das kann auch hintenraus Filter-Arbeit einsparen -> nochmal abgleichen wie das im openehr2csv code derzeit läuft
    aql_path_values = [d.aql_path for d in web_temp_elmnts]


    adjusted_aql_string = generate_aql(aql_path_values)
    resp = util.sendAqlRequest(config.targetAdress, config.targetAuthHeader, "9999999999999", adjusted_aql_string)
    util.storeRespAsCSV(workdir, "compositions_as_csvs", resp, config.templateName+".csv", web_temp_elmnts)

def generate_aql(aql_path_values):
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
# -*- coding: utf-8 -*-
###########################################################################
# PATHS from WebTemplate

# Dieses Skript extrahiert FLAT-Pfade aus einem WebTemplate. Das WebTemplate basiert auf dem simSDT-WebTemplate Format der Firma Better, 
# welches sowohl die Better Platform als auch die EHRBase unterstützt. 
# 
# Die EHRBase bietet FLAT-Funktionalitäten unter dem "ecis"-Endpunkt an. - Stand Version 0.16 (beta)
# 
# Die openEHR-Community plant die Übernahme des simSDT-Formats in den Standard. - https://specifications.openehr.org/releases/ITS-REST/Release-1.0.2/simplified_data_template.html
#
# FLAT-PFADE 
# - FLAT-Pfade erhält man, indem die ID Felder der Elemente des WebTemplate verkettet werden.
# - Feld id enthaelt den Namen des Elements
# - MIN und MAX geben an, wie oft das Element in einer Ressource vorhanden sein kann oder muss. -> Max: -1 = Element kann beliebig oft vorkommen
# - Suffixe werden an den Pfad am Ende angehängt. -> Element/Element2|suffix
#
# Output
# - Ausgabe ist ein Dictionary mit Pfadnamen als key ala dict['Pfadname']['rmType'] und dict['Pfadname']['mandatory']
# - mandatory ist 0 oder 1, wobei 1 = Pflichtfeld bedeutet
###########################################################################

# List of Types and their attributes (X indicates that this one is **definitely** handled in this script)
# https://specifications.openehr.org/releases/RM/latest/data_types.html

# Documentation is here: https://pad.gwdg.de/nGok78r6SCK58rlZttKOAw?both
""" rmType and suffixes that are needed and rough structure
X 1	    PARTY_PROXY	        id, id_scheme, id_namespace, name	    suffix + type	
X 2	    DV_IDENTIFIER	    id, type, issuer, assigner	            suffix + type	
X 3	    DV_QUANTITY 	    magnitude, unit	                        suffix + type   und   suffix + type (+ list)	Intervals have specific Types for their Boundaries
X 4	    DV_TEXT, DV_BOOLEAN, DV_URI, DV_EHR_URI,DV_DATE_TIME, DV_DATE, DV_TIME	none	type	
X 5	    DV_MULTIMEDIA	    none + mediatype + alternatetext + size	    type	
X 6	    DV_PROPORTION	    numerator, denominator, type	        inputs + proportionTypes (under element)	"Type is an Integer which takes the number of the type from the list of types.. 'ratio','unitary','percent','fraction','integer_fraction'
X 7	    CODE_PHRASE	        terminology, code	                    No 'inputs' (under element)	
X 8	    DV_COUNT	        value	                                type + (validation)	
X 9	    DV_ORDINAL	        value, code, ordinal	                type + list	
X 10	DV_CODED_TEXT	    value, code, terminology	            suffix + type	
X 11	DV_PARSABLE	        value, formalism	                        suffix + type	
X 12	DV_DURATION	        year,month,day,week,hour,minute,second		
"""

# TODO
# Es wäre gut auch die Validation-Angaben mitzuschleppen. Bei Elementen, die diese haben. 

###########################################################################
# Standard library imports
from collections import defaultdict
import traceback #debug
# Third party imports
# Local application imports

indent = "    "
case4 = ["DV_TEXT", "DV_BOOLEAN", "DV_URI", "DV_EHR_URI", "DV_DATE_TIME", "DV_DATE", "DV_TIME"]

############################### Main ###############################

def main(webTemp, templateName):

    pathDict = defaultdict(list)
    try:
        # Durchlaufe den Baum
        path = webTemp['tree']['id']
        parentMandatoryChain = ""
        pathDict = goLow(path, pathDict, webTemp['tree']['children'],parentMandatoryChain)

        # Gib some Output
        print ( indent + "Anzahl extrahierter Pfade: " + str( len(pathDict) ) )
    except Exception as e:
        print(indent + templateName + "_Webtemplate ist fehlerhaft.")
        print (indent + str(e))
        traceback.print_exc()
        raise SystemExit

    return pathDict

############################### Methods ###############################

def addSuffixes(pathDict, element, suffixPath, suffixPathArr, mandatoryChain):
    for suffix in suffixPathArr:
        if suffix == "":
            addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath, mandatoryChain)
        else:
            addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath+"|"+suffix, mandatoryChain)

def addPathAndSetRmTypeAndMandatory(pathDict, element, suffixPath, mandatoryChain):
    # Pfade mit Index
    if element['max'] == -1:
        suffixPath += "<<index>>"

    # Pflichtelement oder nicht
    if element['min'] == 1 and '0' in mandatoryChain:
        # Bedingt Mandatory = -1
        pathDict[suffixPath] = { 'rmType' : element['rmType'], 'mandatory' : "-1" }
    elif element['min'] == 1 and not '0' in mandatoryChain:
        pathDict[suffixPath] = { 'rmType' : element['rmType'], 'mandatory' : "1" }
    elif element['min'] == 0:
        pathDict[suffixPath] = { "rmType" : element['rmType'], "mandatory" : "0"  }

    return pathDict

# Rekursiv den Baum durchlaufen
def goLow(parentPath, pathDict, children, parentMandatoryChain):
    self = children
    for element in self:
        # Pfad zum aktuellen Element 
        # Falls Kardinalitaet mehrfacheintraege zulaesst (Max: -1) dann <<index>>
        if element['max'] == -1:
            suffixPath = parentPath + '/' + element['id'] + '<<index>>'
        else:
            suffixPath = parentPath + '/' + element['id']

        # Mandatory
        if element['min'] == 1:
            mandatoryChain = parentMandatoryChain + "/1"
        else:
            mandatoryChain = parentMandatoryChain + "/0"

        # Bei weiteren 'children' tiefer gehen    
        if 'children' in element:
            pathDict = goLow(suffixPath, pathDict, element['children'], mandatoryChain)
        # Falls Element "Inputs" hat -> Gehe jedes Inputs-Element durch und speichere Pfade
        elif 'inputs' in element:
            #print( element['rmType'] )

            # Case 1: PARTY_PROXY -> id, id_scheme, id_namespace, name
            if (element['rmType'] == "PARTY_PROXY"):
                suffixes = ['id','id_scheme','id_namespace','name']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 2: DV_IDENTIFIER -> id, type, issuer, assigner
            elif (element['rmType'] == "DV_IDENTIFIER"):
                suffixes = ['id','type','issuer','assigner']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 3: DV_QUANTITY
            elif (element['rmType'] == "DV_QUANTITY"):
                suffixes = ['magnitude','unit']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 4: DV_TEXT, DV_BOOLEAN, DV_URI, DV_EHR_URI,DV_DATE_TIME, DV_DATE, DV_TIME -> No Suffix
            elif element['rmType'] in case4:
                # No Suffix
                suffixes = ['']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 5: DV_MULTIMEDIA -> none + mediatype + alternatetext + size
            elif element['rmType'] == "DV_MULTIMEDIA":
                # Suffixes
                suffixes = ['','mediatype','alternatetext','size']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 6: DV_PROPORTION -> numerator, denominator, type
            elif element['rmType'] == "DV_PROPORTION":
                suffixes = ['numerator','denominator','type']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 7 is below in the else-Part because there are no "inputs" present

            # Case 8: DV_COUNT
            elif (element['rmType'] == "DV_COUNT"):
                suffixes = ['value']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 9: DV_ORDINAL
            elif (element['rmType'] == "DV_ORDINAL"):
                suffixes = ['value','code','ordinal']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 10: DV_CODED_TEXT 
            elif (element['rmType'] == "DV_CODED_TEXT"):
                suffixes = ['value','code','terminology']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 11: DV_PARSABLE -> value, formalism
            elif (element['rmType'] == "DV_PARSABLE"):
                suffixes = ['value','formalism']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

            # Case 12: DV_DURATION -> year,month,day,week,hour,minute,second	
            elif (element['rmType'] == "DV_DURATION"):
                suffixes = ['year','month','day','week','hour','minute','second']
                addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

        # Case 7: CODE_PHRASE
        elif (element['rmType'] == "CODE_PHRASE"):
            suffixes = ['code','terminology']
            addSuffixes(pathDict, element, suffixPath, suffixes, mandatoryChain)

    return pathDict

if __name__ == '__main__':
    main()
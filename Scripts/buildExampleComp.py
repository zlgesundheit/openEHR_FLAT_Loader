#########################################################################
# Build Example Composition
# Minimal Composition with only mandatory paths
# Maximal Composition with all Paths
#
# Create JSON-String from Dict 
# [Key=Path-Name, Value=data from csv from column that belongs to Path-Name]
# 
# Jendrik Richter (UMG)
#########################################################################

# Standard library imports
import os.path
import json
# Third party imports
import numpy as np
# Local application imports

############################### Main ###############################

def main(workdir, pathArray, templateName, type):

    print ("BuildExampleComp started building a FLAT Example Composition")
    
    buildExample(workdir, pathArray, templateName, type)

    print ("FLAT Example has been built and can be found in Output-Dir \n")

    # TODO To build a CANONICAL Example i need to upload the FLAT Example to the REPO (require config repo baseUrl and config repo authHeader)

############################### Methods ###############################

def buildExample(workdir, pathArray, templateName, type):
    if type == "min":
        
        #Build Resource-Dict mit allen Pflichtpfaden
        dict = {}
        for path in pathArray:
            if path.isMandatory:
                # Dict["Pfad"] = valid Example-Value 
                if path.hasSuffix:
                    for suffix in path.suffixList:
                        dict[path.pathString + "|" + suffix] = path.exampleValue
                elif not path.hasSuffix:
                    dict[path.pathString] = path.exampleValue

        # Store Example-Composition
        filePath = os.path.join(workdir, 'Output', "EXAMPLE_"+ templateName + ".json" )
        with open(filePath,"w", encoding = 'UTF-8') as resFile:
            json.dump(dict, resFile, default=convert, indent=4, ensure_ascii=False)

        print ("\t" + f' FLAT Example-Composition erstellt und im Ordner "Output" gespeichert. \n')

    elif type == "max":
        pass

# Workaround because Pandas uses some panda data types that are NOT serializable. Use like json.dumps(dictArray[0]), default=convert)
def convert(o):
    if isinstance(o, np.int64): return o.item()  
    raise TypeError
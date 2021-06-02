############################### DEV: PATHS from WebTemplate
# Notes:
# Pfad-Teile stehen im Feld id
# Nachfolgende Pfad-Teile bis zu einem Blatt stehen in children

# Suffixe
  # Jeder Suffix ist ein eigenes Feld mit Pfad

  # Blätter mit nur einem Input haben manchmal Suffix
  # Inputs haben oft Suffix-Angaben die mit |suffix and den Pfad angehängt werden

# Kardinalität:
  # Pflicht felder haben min=max=1
  # Felder mit <<index>> haben min:0 max -1 !

import json
import os

def goLow(parentPath, pathArr, children):
  self = children
  for element in self:
    # Fuer jeden Eintrag den Pfad erweitern
    # Falls Kardinalitaet mehrfacheintraege zulaesst (Max: -1) dann <<index>>
    if str(element['max']) == str(-1):
      selfPath = parentPath + '/' + element['id'] + '<<index>>'
    else:
      selfPath = parentPath + '/' + element['id']
    childArr = []
    for key in element:
      childArr.append(key)
    # Falls Element Kinder hat goLow
    if 'children' in childArr:
      pathArr = goLow(selfPath, pathArr, element['children'])
    # Falls Element Inputs hat, speichere Pfad fuer jeden Suffix
    elif 'inputs' in childArr:
      for inputElement in element['inputs']:
        childArr = []
        for key in inputElement:
          childArr.append(key)
        if 'suffix' in childArr:
          suffixPath = parentPath + '/' + element['id'] + '|' + inputElement['suffix']
          pathArr.append(suffixPath)
        # Falls Element Input hat aber keine Suffixe fuege Pfad hinzu
        else:
          suffixPath = parentPath + '/' + element['id']
          pathArr.append(suffixPath)
    # Wenn Element weder Kinder noch inputs hat fuege pfad mit "Standard"-Suffixen hinzu
    else:
      pathArr.append(selfPath + '|code')
      pathArr.append(selfPath + '|terminology')
  return pathArr

def getPathsFromWebTemplate(workdir, templateName):
  filePath = os.path.join(workdir, 'Input', templateName +'_WebTemplate.json')
  f = open(filePath, "r", encoding='utf-8')
  webTemp = f.read()
  f.close()
  webTemp = json.loads(webTemp)

  path = ''
  pathArr = []
  path = webTemp['tree']['id']
  pathArr = goLow(path, pathArr, webTemp['tree']['children'])

  return pathArr